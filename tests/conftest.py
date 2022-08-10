import pytest
import shutil
import tempfile

from suitable import Api
from suitable.mitogen import Api as MitogenApi
from suitable.mitogen import is_mitogen_supported


if is_mitogen_supported():
    APIS = ('vanilla', 'mitogen')
else:
    APIS = ('vanilla', ) # type: ignore


class Container(object):

    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def spawn_api(self, api_class, **kwargs):
        options = {
            'connection': 'smart',
            'extra_vars': {
                'ansible_python_interpreter': '/usr/bin/python3'
            }
        }

        hosts = {
                "suitable": {
                    "ansible_host": self.host,
                    "ansible_port": self.port,
                    "ansible_ssh_user": self.username,
                    "ansible_ssh_pass": self.password,
               }
            }

        options.update(kwargs)
        api_instance = api_class(servers=hosts, verbosity="info", options=options)
        return api_instance


    def vanilla_api(self, **kwargs):
        return self.spawn_api(Api, **kwargs)

    def mitogen_api(self, **kwargs):
        return self.spawn_api(MitogenApi, **kwargs)


@pytest.fixture(scope="function")
def tempdir():
    tempdir = tempfile.mkdtemp()
    yield tempdir
    shutil.rmtree(tempdir)


@pytest.fixture(scope="function")
def container():
    yield Container('localhost', "9999", 'root', 'root')

@pytest.fixture
def target_a():
    target_host = {"target_a": {"ansible_host": "localhost", "ansible_port": "8888", "ansible_ssh_user": "root", "ansible_ssh_pass": "root"}}
    return target_host

@pytest.fixture
def target_b():
    target_host = {"target_b": {"ansible_host": "localhost", "ansible_port": "9999", "ansible_ssh_user": "root", "ansible_ssh_pass": "root"}}
    return target_host


@pytest.fixture(scope="function", params=APIS)
def api(request, container):
    yield getattr(container, '%s_api' % request.param)(connection='paramiko')
