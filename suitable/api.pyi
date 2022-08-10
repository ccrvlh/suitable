import typing as t

from ansible import constants as C

class Api(object):
    def package(
        self,
        name: str,
        version: t.Optional[str] = None,
        state: str = "present",
        **options
    ):
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
