import logging
import os
import typing as t
from contextlib import contextmanager

from ansible import constants as C
from ansible.plugins.loader import module_loader, strategy_loader

from suitable.errors import ModuleError, UnreachableError
from suitable.inventory import Inventory
from suitable.module_runner import ModuleRunner
from suitable.utils import LOG_VERBOSITY, options_as_class


class Api(object):
    """
    Provides all available ansible modules as local functions::
    
    Example::

        ..codeblock::python
            >>> from suitable import Api
            >>> api = Api('personal.server.dev')
            >>> api.sync(src='/Users/denis/.zshrc', dest='/home/denis/.zshrc')

    """
    def __init__(
        self, servers: t.Union[str, t.List[t.Any], t.Dict[str, dict]],
        ignore_unreachable: bool = False,
        ignore_errors: bool = False,
        host_key_checking: bool = True,
        sudo: bool = False,
        dry_run: bool = False,
        verbosity: str = 'info',
        environment=None,
        strategy=None,
        **options
    ):
        """
        :param servers:
            A list of servers, a string with space-delimited servers or a dict
            with server name as key and ansible host variables as values. The
            api instances will operate on these servers only. Servers which
            cannot be reached or whose use triggers an error are taken out
            of the list for the lifetime of the object.

            Examples of valid uses::

                api = Api(['web.example.org', 'db.example.org'])
                api = Api('web.example.org')
                api = Api('web.example.org db.example.org')
                api = Api({'web.example.org': {'ansible_host': '10.10.5.1'}})
                api = Api(['example.org:2222', 'example.org:2223'])


        :param ignore_unreachable:
            If true, unreachable servers will not trigger an exception. They
            are however still taken out of the list for the lifetime of the
            object.

        :param ignore_errors:
            If true, errors on servers will not trigger an exception. Servers
            who trigger an error are still ignored for the lifteime of the
            object.

        :param sudo:
            If true, the commands run as root using sudo. This is a shortcut
            for the following::

                Api('example.org', become=True, become_user='root')

            If ``become`` or ``become_user`` are passed, this option is
            ignored!

        :param sudo_pass:
            If given, sudo is invoked with the given password. Alternatively
            you can use Ansible's builtin password option (e.g.
            ``passwords={'become_pass': '***'}``).

        :param remote_pass:
            Passwords are passed to ansible using the passwords dictionary
            by default (e.g. ``passwords={'conn_pass': '****'}``). Since this
            is a bit cumbersome and because earlier Suitable releases supported
            `remote_pass` this convenience argument exists.

            If `passwords` is passed, the `remote_pass` argument is ignored.

        :param dry_run:
            Runs ansible in 'check' mode, where no changes are actually
            applied to the server(s).

        :param verbosity:
            The verbosity level of ansible. Possible values:

            * ``debug``
            * ``info`` (default)
            * ``warn``
            * ``error``
            * ``critical``

        :param environment:
            The environment variables which should be set during when
            a module is executed. For example::

                api = Api('example.org', environment={
                    'PGPORT': '5432'
                })

        :param strategy:
            The Ansible strategy to use. Defaults to None which lets Ansible
            decide which strategy it wants to use.

            Note that you need to globally install strategy plugins using
            :meth:`install_strategy_plugins` before using strategies provided
            by plugins.

        :param host_key_checking:
            Set to false to disable host key checking.

        :param extra_vars:

            Extra variables available to Ansible. Note that those will be
            global and not bound to any particular host::

                api = Api('webserver', extra_vars={'home': '/home/denis'})
                api.file(dest="{{ home }}/.zshrc", state='touch')

            This can be used to specify an alternative Python interpreter::

                api = Api('example.org', extra_vars={
                    'ansible_python_interpreter': '/path/to/interpreter'
                })

        :param ``**options``:
            All remining keyword arguments are passed to the Ansible
            TaskQueueManager. The available options are listed here:

            `<http://docs.ansible.com/ansible/developing_api.html>`_

        """
        ...
    
    def package(self, name: str, version: t.Opional[str] =None, state: str = 'present', **options):
        """
        Installs a package.

        :param name:
            The name of the package.

        :param version:
            The version of the package. If not given, the latest version is
            installed.

        :param state:
            The state of the package. Possible values:

            * ``present`` (default)
            * ``absent``
            * ``latest``
            * ``upgraded``

        :param ``**options``:
            All remaining keyword arguments are passed to the Ansible
            module. The available options are listed here:

            `<http://docs.ansible.com/ansible/developing_api.html>`_

        """
        ...

    def on_unreachable_host(self, module, host): 
        """ If you want to customize your error handling, this would be
        the point to write your own method in a subclass.

        Note that this method is not called if ignore_unreachable is True.

        If the return value of this method is 'keep-trying', the server
        will not be ignored for the lifetime of the object. This enables
        you to practically write your own flavor of 'ignore_unreachable'.

        If an any exception is raised the server WILL be ignored.

        """
        ...

    def on_module_error(self, module, host, result):
        """ If you want to customize your error handling, this would be
        the point to write your own method in a subclass.

        Note that this method is not called if ignore_errors is True.

        If the return value of this method is 'keep-trying', the server
        will not be ignored for the lifetime of the object. This enables
        you to practically write your own flavor of 'ignore_errors'.

        If an any exception is raised the server WILL be ignored.

        """
        ...

    def is_valid_return_code(self, code):
        ...

    @contextmanager
    def valid_return_codes(self, *codes):
        """ Sets codes which are considered valid when returned from
        command modules. The default is (0, ).

        Should be used as a context::

            with api.valid_return_codes(0, 1):
                api.shell('test -e /tmp/log && rm /tmp/log')

        """
        ...



def install_strategy_plugins(directories):
    """ Loads the given strategy plugins, which is a list of directories,
    a string with a single directory or a string with multiple directories
    separated by colon.

    As these plugins are globally loaded and cached by Ansible we do the same
    here. We could try to bind those plugins to the Api instance, but that's
    probably not something we'd ever have much of a use for.

    Call this function before using custom strategies on the :class:`Api`
    class.

    """
    ...

def list_ansible_modules():
    # inspired by
    # https://github.com/ansible/ansible/blob/devel/bin/ansible-doc

    ...

def get_modules_from_path(path):
    ...
