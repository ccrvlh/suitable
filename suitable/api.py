import typing as t

from ansible import constants as C
from contextlib import contextmanager
from suitable.errors import UnreachableError
from suitable.errors import ModuleError
from suitable.runner import ModuleRunner
from suitable.results import RunnerResults
from suitable.utils import list_ansible_modules
from suitable.utils import options_as_class
from suitable.utils import VERBOSITY
from suitable.inventory import Inventory


class Api(object):
    """
    Provides all available ansible modules as local functions::

        api = Api('personal.server.dev')
        api.sync(src='/Users/denis/.zshrc', dest='/home/denis/.zshrc')

    """

    def __init__(
        self,
        servers,                    # type: t.Optional[dict[t.Any, t.Any]]
        ignore_unreachable=False,   # type: bool
        ignore_errors=False,        # type: bool
        host_key_checking=False,    # type: bool
        sudo=False,                 # type: bool
        dry_run=False,              # type: bool
        verbosity='info',           # type: str
        environment=None,           # type: dict[t.Any, t.Any]
        strategy=None,              # type: str
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
        # Initial Config
        # Keeps host_key_checking around for the runner
        self.inventory = Inventory(options.get('connection', None), hosts=servers)
        self.host_key_checking = host_key_checking
        self._valid_return_codes = (0, )
        self.ignore_unreachable = ignore_unreachable
        self.ignore_errors = ignore_errors
        self.environment = environment or {}
        self.strategy = strategy

        # Set Options
        options = self._set_initial_options(options, sudo)
        options = self._set_required_options(options)
        options = self._set_default_options(options, verbosity, dry_run)
        options = self._set_options_passwords(options)
        self.options = options_as_class(options)
        self._hook_modules()

    def _hook_modules(self):
        """
        Hook modules dynamically adds Ansible's modules
        to the API Class, making it possible to access modules
        without declaring each on of them here.

        Example::

            >>> ansible = Api(host)
            >>> ansible.shell("whoami")
        """        
        for runner in (ModuleRunner(m) for m in list_ansible_modules()):
            runner.hookup(self)

    def _set_initial_options(self, options, sudo):
        """Inital options configuration include:
            - Setting the connection
            - Adding a `sudo` shortcut
            - Asserting `module_path` is not being used (not supported)

        Args:
            options (dict): The main options dictionary
            sudo (bool): Whether to use sudo

        Returns:
            options (dict): the options dictionary
        """
        if 'connection' not in options:
            options['connection'] = 'smart'

        if not ('become' in options or 'become_user' in options):
            options['become'] = sudo
            options['become_user'] = 'root'

        assert 'module_path' not in options, """
            Suitable does not yet support the setting of a custom module path.
            Please create an issue if you need this feature!
        """
        options['module_path'] = None
        return options

    def _set_options_passwords(self, options):
        """Sets passwords to the options dict.
        If the user hasn't set a password, it will
        use `remote_pass` / `conn_pass` for the connection
        or `sudo_pass` / `become_pass` for the root.

        Args:
            options (dict): The options dictionary

        Returns:
            options (dict): The fixed options dictionary
        """        
        if 'passwords' in options:
            return options
        
        connection_pass = options.get('remote_pass') or options.get('conn_pass')
        become_pass = options.get('sudo_pass') or options.get('become_pass')
        
        options['passwords'] = {
            'conn_pass': connection_pass,
            'become_pass': become_pass
        }
        return options

    def _set_required_options(self, options):
        """Loads all defaults required by Ansible.
        Includes the available constants

        Args:
            options (dict): The options dict

        Returns:
            options (dict): The options dict
        """
        required_defaults = (
            'forks',
            'remote_user',
            'private_key_file',
            'become',
            'become_method',
            'become_user'
        )

        for default in required_defaults:
            if default in options:
                continue
            options[default] = getattr(
                C, 'DEFAULT_{}'.format(default.upper())
            )
        return options

    def _set_default_options(self, options, verbosity, dry_run):
        """Not all options seem to have accessible defaults.

        Args:
            options (dict): Options dict
            verbosity (_type_): Verbosity level
            dry_run (bool): Whether to dry run

        Returns:
            options: The Options dict
        """
        options['ssh_common_args'] = options.get('ssh_common_args', None)
        options['ssh_extra_args'] = options.get('ssh_extra_args', None)
        options['sftp_extra_args'] = options.get('sftp_extra_args', None)
        options['scp_extra_args'] = options.get('scp_extra_args', None)
        options['extra_vars'] = options.get('extra_vars', {})
        options['diff'] = options.get('diff', False)
        options['verbosity'] = VERBOSITY.get(verbosity)
        options['check'] = dry_run
        return options

    def on_unreachable_host(self, module, host):
        # type: (str, str) -> None
        """ If you want to customize your error handling, this would be
        the point to write your own method in a subclass.

        Note that this method is not called if ignore_unreachable is True.

        If the return value of this method is 'keep-trying', the server
        will not be ignored for the lifetime of the object. This enables
        you to practically write your own flavor of 'ignore_unreachable'.

        If an any exception is raised the server WILL be ignored.

        """
        raise UnreachableError(module, host)

    def on_module_error(self, module, host, result):
        # type: (str, str, RunnerResults) -> None
        """ If you want to customize your error handling, this would be
        the point to write your own method in a subclass.

        Note that this method is not called if ignore_errors is True.

        If the return value of this method is 'keep-trying', the server
        will not be ignored for the lifetime of the object. This enables
        you to practically write your own flavor of 'ignore_errors'.

        If an any exception is raised the server WILL be ignored.

        """
        raise ModuleError(module, host, result)

    def is_valid_return_code(self, code):
        # type: (int) -> bool
        return code in self._valid_return_codes

    @contextmanager
    def valid_return_codes(self, *codes):
        # type: (*t.Any) -> t.Iterator[t.Any]
        """
        Sets codes which are considered valid when returned from
        command modules. The default is (0, ).

        Should be used as a context::

            with api.valid_return_codes(0, 1):
                api.shell('test -e /tmp/log && rm /tmp/log')

        """
        previous_codes = self._valid_return_codes
        self._valid_return_codes = codes # type: ignore
        yield
        self._valid_return_codes = previous_codes
