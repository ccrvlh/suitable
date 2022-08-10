from ansible.inventory.manager import InventoryManager

from suitable.compat import string_types # type: ignore


class Inventory(dict):

    def __init__(self, ansible_connection=None, hosts=None):
        # type: (str, dict) -> None
        super(Inventory, self).__init__()
        self.ansible_connection = ansible_connection
        if hosts:
            self.add_hosts(hosts)

    def add_host(self, server, host_variables):
        # type: (str, dict) -> None
        self[server] = {}

        # [ipv6]:port
        if server.startswith('['):
            host, port = server.rsplit(':', 1)
            self[server]['ansible_host'] = host = host.strip('[]')
            self[server]['ansible_port'] = int(port)

        # host:port
        elif server.count(':') == 1:
            host, port = server.split(':', 1)
            self[server]['ansible_host'] = host
            self[server]['ansible_port'] = int(port)

        # Add vars
        self[server].update(host_variables)

        # Localhost
        if not self.ansible_connection:
            # Get hostname (either ansible_host or server)
            is_default_ssh_port = self[server].get('ansible_port', 22) == 22
            host = self[server].get('ansible_host', server)
            if host in ('localhost', '127.0.0.1', '::1') and is_default_ssh_port:
                self[server]['ansible_connection'] = 'local'
                print("HERE!!!")

    def add_hosts(self, servers):
        # type: (dict) -> None
        if isinstance(servers, string_types):
            for server in servers.split(u' '):
                self.add_host(server, {})
        elif isinstance(servers, dict):
            for server, host_variables in servers.items():
                self.add_host(server, host_variables)
        else:
            for server in servers:
                self.add_host(server, {})


class SourcelessInventoryManager(InventoryManager):
    """
    A custom inventory manager that turns the source parsing into a noop.

    Without this, Ansible will warn that there are no inventory sources that
    could be parsed. Naturally we do not have such sources, rendering this
    warning moot.
    """

    def parse_sources(self, *args, **kwargs):
        pass
