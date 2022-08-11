"""
List of old Core maitained packages: https://docs.ansible.com/ansible/2.4/core_maintained.html
Still need to find the new ones.

This provides autocomplete and type stubs for the existing Ansible Core modules. Community module will not be supported.
Assess the viability of building types and docstring automatically from Ansible module documentation.
Example (AptKey Module)::

    description:
    - Add or remove an I(apt) key, optionally downloading it.
    options:
        id:
            description:
                - The identifier of the key.
                - Including this allows check mode to correctly report the changed state.
                - If specifying a subkey's id be aware that apt-key does not understand how to remove keys via a subkey id.  Specify the primary key's id instead.
                - This parameter is required when C(state) is set to C(absent).
            type: str
        data:
            description:
                - The keyfile contents to add to the keyring.
            type: str
        file:
            description:
                - The path to a keyfile on the remote server to add to the keyring.
            type: path
        keyring:
            description:
                - The full path to specific keyring file in C(/etc/apt/trusted.gpg.d/).
            type: path
            version_added: "1.3"
        url:
            description:
                - The URL to retrieve key from.
            type: str
        keyserver:
            description:
                - The keyserver to retrieve key from.
            type: str
            version_added: "1.6"
        state:
            description:
                - Ensures that the key is present (added) or absent (revoked).
            type: str
            choices: [ absent, present ]
            default: present
        validate_certs:
            description:
                - If C(no), SSL certificates for the target url will not be validated. This should only be used
                on personally controlled sites using self-signed certificates.
            type: bool
            default: 'yes'


Would become::

    def module(self, id: str, data: str, file: str, keyring: str, url: str, keyserver: str, state: str, validate_certs: bool):
        "
         Add or remove an I(apt) key, optionally downloading it.

            :param id (str): The identifier of the key.
            :param data: The keyfile contents to add to the keyring.
            :param file: The path to a keyfile on the remote server to add to the keyring.
            :param keyring: The full path to specific keyring file in C(/etc/apt/trusted.gpg.d/).
            :param url: The URL to retrieve key from.
            :param keyserver: The keyserver to retrieve key from.
            :param state: Ensures that the key is present (added) or absent (revoked). [ absent, present ]
            :param validate_certs: If C(no), SSL certificates for the target url will not be validated. This should only be used on personally controlled sites using self-signed certificates.
            :returns:
            :rtype:
        "

"""
import typing as t

from ansible import constants as C

class Api(object):
    def package(
        self, name: str, version: t.Optional[str] = None, state: str = "present", **options
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
    def acl(self): ...
    def add_host(self): ...
    def apt(self): ...
    def apt_key(self): ...
    def apt_repository(self): ...
    def assemble(self): ...
    def assert_(self): ...
    def async_status(self): ...
    def at(self): ...
    def authorized_key(self): ...
    def aws_s3(self): ...
    def blockinfile(self): ...
    def cloudformation(self): ...
    def command(self): ...
    def copy(self): ...
    def debconf(self): ...
    def debug(self): ...
    def dnf(self): ...
    def ec2(self): ...
    def ec2_group(self): ...
    def ec2_metadata_facts(self): ...
    def ec2_snapshot(self): ...
    def ec2_vol(self): ...
    def ec2_vpc_net(self): ...
    def ec2_vpc_net_facts(self): ...
    def ec2_vpc_subnet(self): ...
    def ec2_vpc_subnet_facts(self): ...
    def fail(self): ...
    def fetch(self): ...
    def file(self): ...
    def find(self): ...
    def get_url(self): ...
    def getent(self): ...
    def git(self): ...
    def group(self): ...
    def group_by(self): ...
    def import_playbook(self): ...
    def import_role(self): ...
    def import_tasks(self): ...
    def include(self): ...
    def include_role(self): ...
    def include_tasks(self): ...
    def include_vars(self): ...
    def iptables(self): ...
    def lineinfile(self): ...
    def meta(self): ...
    def mount(self): ...
    def pause(self): ...
    def ping(self): ...
    def pip(self): ...
    def raw(self): ...
    def rhn_channel(self): ...
    def rpm_key(self): ...
    def s3_bucket(self): ...
    def script(self): ...
    def seboolean(self): ...
    def selinux(self): ...
    def service(self): ...
    def set_fact(self): ...
    def setup(self): ...
    def shell(self): ...
    def slurp(self): ...
    def stat(self): ...
    def subversion(self): ...
    def synchronize(self): ...
    def sysctl(self): ...
    def systemd(self): ...
    def template(self): ...
    def unarchive(self): ...
    def uri(self): ...
    def user(self): ...
    def wait_for(self): ...
    def wait_for_connection(self): ...
    def win_acl(self): ...
    def win_acl_inheritance(self): ...
    def win_command(self): ...
    def win_copy(self): ...
    def win_disk_image(self): ...
    def win_dns_client(self): ...
    def win_domain(self): ...
    def win_domain_controller(self): ...
    def win_domain_membership(self): ...
    def win_file(self): ...
    def win_get_url(self): ...
    def win_group(self): ...
    def win_owner(self): ...
    def win_package(self): ...
    def win_path(self): ...
    def win_ping(self): ...
    def win_reboot(self): ...
    def win_regedit(self): ...
    def win_service(self): ...
    def win_share(self): ...
    def win_shell(self): ...
    def win_stat(self): ...
    def win_template(self): ...
    def win_updates(self): ...
    def win_user(self): ...
    def yum(self): ...
    def yum_repository(self): ...
