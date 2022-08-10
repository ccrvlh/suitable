import port_for # type: ignore
import pytest
import shutil
import subprocess
import tempfile

from uuid import uuid4
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
        # return api_class(
        #     '%s:%s' % (self.host, self.port),
        #     ** options
        # )

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
#     port = port_for.select_random()
#     name = 'suitable-container-%s' % uuid4().hex

#     subprocess.check_call((
#         'docker', 'run', '-d', '--rm', '-it', '--name', name,
#         '-p', 'localhost:%d:2222/tcp' % port,
#         'rastasheep/ubuntu-sshd:18.04'
#     ))

    yield Container('localhost', "2222", 'root', 'root')

#     subprocess.call(('docker', 'stop', name))


@pytest.fixture(scope="function", params=APIS)
def api(request, container):
    yield getattr(container, '%s_api' % request.param)(connection='paramiko')
