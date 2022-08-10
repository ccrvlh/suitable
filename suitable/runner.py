from __main__ import display

import atexit
import logging
import os
import signal
import sys
import typing as t
import ansible.constants

from contextlib import contextmanager
from datetime import datetime
from pprint import pformat

from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from ansible.playbook.play import Play
from ansible.vars.manager import VariableManager

from suitable.callback import SilentCallbackModule
from suitable.utils import log
from suitable.results import RunnerResults

try:
    from ansible import context
except ImportError:
    set_global_context = None
else:
    set_global_context = context._init_global_context


if t.TYPE_CHECKING:
    from suitable.api import Api


@contextmanager
def ansible_verbosity(verbosity):
    # type: (int) -> t.Generator[None, None, None]
    """
    Temporarily changes the ansible verbosity. Relies on a single display
    instance being referenced by the __main__ module.

    This is setup when suitable is imported, though Ansible could already
    be imported beforehand, in which case the output might not be as verbose
    as expected.

    To be sure, import suitable before importing ansible. ansible.

    """
    previous = display.verbosity
    display.verbosity = verbosity
    yield
    display.verbosity = previous


@contextmanager
def environment_variable(key, value):
    # type: (str, t.Any) -> t.Iterator[t.Any]
    """ Temporarily overrides an environment variable. """

    previous = None
    if key in os.environ:
        previous = os.environ[key]
    os.environ[key] = value

    yield

    if previous is None:
        del os.environ[key]
    else:
        os.environ[key] = previous


@contextmanager
def host_key_checking(enable):
    # type: (bool) -> t.Iterator[t.Any]
    """ Temporarily disables host_key_checking, which is set globally. """

    def as_string(b):
        return b and 'True' or 'False'

    with environment_variable('ANSIBLE_HOST_KEY_CHECKING', as_string(enable)):
        previous = ansible.constants.HOST_KEY_CHECKING
        ansible.constants.HOST_KEY_CHECKING = enable
        yield
        ansible.constants.HOST_KEY_CHECKING = previous


class SourcelessInventoryManager(InventoryManager):
    """
    A custom inventory manager that turns the source parsing into a noop.

    Without this, Ansible will warn that there are no inventory sources that
    could be parsed. Naturally we do not have such sources, rendering this
    warning moot.
    """

    def parse_sources(self, *args, **kwargs):
        pass


class ModuleRunner(object):

    def __init__(self, module_name):
        # type: (str) -> None
        """
        Runs any ansible module given the module's name and access
        to the api instance (done through the hookup method).
        """
        self.module_name = module_name
        self.api = None
        self.module_args = None

    def __str__(self):
        """
        Return a represenation of the module, including the last
        run module_args (-> this will end up looking a lot like) an entry
        in an ansible yaml file.
        """
        return "{}: {}".format(self.module_name, self.module_args)

    @property
    def is_hooked_up(self):
        """
        Checks whether the module being called by the `Api` is hooked up.

        Returns:
            bool: True if is hooked up, False otherwise.
        """        
        return self.api is not None and hasattr(self.api, self.module_name)

    def hookup(self, api):
        # type: (Api) -> None
        """Hooks the module to the given API

        Args:
            api (Api): The API Client.
        """
        if api is None:
            raise ValueError('The API is not valid')
        assert not hasattr(api, self.module_name), """
            '{}' conflicts with existing attribute
        """.format(self.module_name)

        self.api = api # type: ignore

        setattr(api, self.module_name, self.execute)

    def get_module_args(self, args, kwargs):
        """
        Get the module arguments.
        Escapes equalities signs until this is fixed:
        https://github.com/ansible/ansible/issues/13862

        Args:
            args (_type_): _description_
            kwargs (_type_): _description_

        Returns:
            _type_: _description_
        """
        args = u' '.join(args).replace('=', '\\=')

        kwargs = u' '.join(u'{}="{}"'.format(
            k, v.replace('"', '\\"')) for k, v in kwargs.items())

        return u' '.join((args, kwargs)).strip()

    def _build_play_source(self, module_args):
        # type: (str) -> dict[str, t.Any]
        if self.api is None:
            raise ValueError('API must be hooked up')

        play_source = {
            'name': "Suitable Play",
            'hosts': 'all',
            'gather_facts': 'no',
            'tasks': [{
                'action': {
                    'module': self.module_name,
                    'args': module_args,
                },
                'environment': self.api.environment,
            }]
        }
        return play_source

    def _build_inventory_manager(self, loader):
        # type: (DataLoader) -> InventoryManager
        """
        Given the API Inventoy, builds Ansible's InventoryManager.
        It will iterate the inventory, add hosts to the manager and set variables
        for each of the hosts.

        Returns:
            _type_: _description_
        """        
        if not self.api:
            raise AttributeError("Can't build inventory. The API is not hooked up.")
        
        inventory_manager = SourcelessInventoryManager(loader=loader)
        for host, host_variables in self.api.inventory.items():
            inventory_manager._inventory.add_host(host, group='all')
            for key, value in host_variables.items():
                inventory_manager._inventory.set_variable(host, key, value)

        for key, value in self.api.options.extra_vars.items():
            inventory_manager._inventory.set_variable('all', key, value)

        return inventory_manager

    def execute(self, *args, **kwargs):
        """
        Puts args and kwargs in a way ansible can understand. Calls ansible
        and interprets the result.

        Note on verbosity:
        Ansible uses various levels of verbosity (from -v to -vvvvvv)
        offering various amounts of debug information
        we keep it a bit simpler by activating all of it during debug,
        and falling back to the default of 0 otherwises.

        Note on host_key_cheking:
        host_key_checking is special, since not each connection
        plugin handles it the same way, we need to apply both
        environment variable and Ansible constant when running a
        command in the runner to be successful

        Note on System Exit:
        Mitogen forks our process and exits it in one
        instance before returning
        
        This is fine, but it does lead to a very messy exit
        by py.test which will essentially return with a test
        that is first successful and then failed as each
        forked process dies.
        
        To avoid this we commit suicide if we are run inside
        a pytest session. Normally this would just result
        in a exit code of zero, which is good.

        Note on Global Context:
        Ansible 2.8 introduces a global context which persists
        during the lifetime of the process - for Suitable this
        singleton/cache needs to be cleared after each call
        to make sure that API calls do not carry over state.
        
        The docs hint at a future inclusion of local contexts, which
        would of course be preferable.

        """
        # Initialize Execution
        start = datetime.utcnow()
        task_queue_manager = None
        callback = SilentCallbackModule()
        loader = DataLoader()

        # Initial checks
        assert self.is_hooked_up, "The module should be hooked up to the api"
        if set_global_context:
            set_global_context(self.api.options)

        # Build the module arguments
        self.module_args = kwargs
        if args:
            self.module_args = self.get_module_args(args, kwargs)

        # Inventory & Playbook
        inventory_manager = self._build_inventory_manager(loader)
        variable_manager = VariableManager(loader=loader, inventory=inventory_manager)
        play_source = self._build_play_source(self.module_args)
        play = Play.load(play_source, variable_manager=variable_manager, loader=loader)

        if self.api.strategy:
            play.strategy = self.api.strategy

        log.info(
            u'running {}'.format(u'- {module_name}: {module_args}'.format(
                module_name=self.module_name,
                module_args=self.module_args
            ))
        )

        try:
            verbosity = self.api.options.verbosity == logging.DEBUG and 6 or 0
            with ansible_verbosity(verbosity):
                with host_key_checking(self.api.host_key_checking):
                    kwargs = dict(
                        inventory=inventory_manager,
                        variable_manager=variable_manager,
                        loader=loader,
                        options=self.api.options,
                        passwords=getattr(self.api.options, 'passwords', {}),
                        stdout_callback=callback
                    )

                    if set_global_context:
                        del kwargs['options']

                    task_queue_manager = TaskQueueManager(**kwargs)

                    try:
                        task_queue_manager.run(play)
                    except SystemExit:
                        if 'pytest' in sys.modules:
                            try:
                                atexit._run_exitfuncs()
                            except Exception:
                                pass
                            os.kill(os.getpid(), signal.SIGKILL)

                        raise
        finally:
            if task_queue_manager is not None:
                task_queue_manager.cleanup()

            if set_global_context:
                from ansible.utils.context_objects import GlobalCLIArgs
                GlobalCLIArgs._Singleton__instance = None

        log.debug(u'took {} to complete'.format(datetime.utcnow() - start))
        return self.evaluate_results(callback)

    def ignore_further_calls_to_server(self, server: str):
        """
        Ignore further calls to the given server.

        Args:
            server (str): The server to ignore.
        """
        if not self.api:
            raise AttributeError('The API is not yet hooked up')
        log.error(u'ignoring further calls to {}'.format(server))
        del self.api.inventory[server]

    def trigger_event(self, server, method, args):
        # type: (str, str, tuple[t.Any, ...]) -> None
        """
        Trigers an event based based on the server and method.

        Args:
            server (str): The server to trigger the event on.
            method (str): The method to trigger the event on.
            args (tuple[t.Any, ...]): Arguments
        """        
        try:
            action = getattr(self.api, method)(*args)
            if action != 'keep-trying':
                self.ignore_further_calls_to_server(server)

        except Exception:
            self.ignore_further_calls_to_server(server)
            raise

    def evaluate_results(self, callback):
        # type: (SilentCallbackModule) -> RunnerResults
        """
        Prepare the result of runner call for use with RunnerResults.
        If none of the modules in our tests hit the 'failed' result
        codepath (which seems to not be implemented by all modules)
        so we ignore this branch since it's rather trivial.

        Review RunnerResults:
        This is a weird structure because RunnerResults still works
        like it did with Ansible 1.x, where the results where structured
        like this.

        Args:
            callback (SilentCallbackModule): The callback to use.

        Raises:
            AttributeError: If the API is not hooked up

        Returns:
            RunnerResults: A RunnerResults (dict) instance.
        """
        if not self.api:
            raise AttributeError('The API is not yet hooked up')

        contacted_servers: dict[str, t.Any] = callback.contacted
        unreacheable_servers: dict[str, t.Any] = callback.unreachable

        for server, result in unreacheable_servers.items():
            log.error(u'{} could not be reached'.format(server))
            log.debug(u'ansible-output =>\n{}'.format(pformat(result)))

            if self.api.ignore_unreachable:
                continue

            self.trigger_event(server, 'on_unreachable_host', (
                self, server
            ))

        for server, answer in contacted_servers.items():
            success: bool = answer['success']
            result: dict[t.Any, t.Any] = answer['result'] # type: ignore

            if result.get('failed'):  # pragma: no cover
                success = False

            if 'rc' in result:
                if self.api.is_valid_return_code(result['rc']):
                    success = True

            result['success'] = success
            if success:
                continue

            log.error(u'{} failed on {}'.format(self, server))
            log.debug(u'ansible-output =>\n{}'.format(pformat(result)))

            if self.api.ignore_errors:
                continue

            self.trigger_event(server, 'on_module_error', (
                self, server, result
            ))

        results = RunnerResults({
            'contacted': {
                server: answer['result']
                for server, answer in contacted_servers.items()
            },
            'unreachable': {
                server: result
                for server, result in unreacheable_servers.items()
            }
        })

        return results
