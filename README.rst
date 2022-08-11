.. image:: https://cdn.jsdelivr.net/gh/seantis/suitable@master/docs/source/_static/logo.svg
    :alt: Suitable
    :width: 50%
    :align: center

An Ansible API for humans.

Documentation
-------------

`<http://suitable.readthedocs.org>`_

Quick Start
-------------

Suitable provides a simple wrapper over Ansible's internal API, that allows to use Ansible programatically.

.. code-block:: python

    >>> api = Api('personal.server.dev')
    >>> api.shell("whoami")
    myuser


Warning
-------

Suitable is not endorsed by Ansible and it is not affilated with it. Use at
your own peril.

The official way to use Ansible from Python is documented here:
`<http://docs.ansible.com/ansible/developing_api.html>`_

Compatibility
-------------

* Python 3.5+ (only automated tests with 3.7+)
* Ansible 2.8+
* Mitogen 0.2.6+ (currently incompatible with Ansible 2.8)

Support for older releases is kept only if possible. New Ansible releases
are favored over old ones.

Currently tested Ansible versions:
- Ansible: 2.8, 2.9, 2.10, 4.x, 5.x, 6.x
- Ansible Core: 2.8, 2.9, 2.10, 2.12, 2.13


Run Tests
---------

For convenience a Dockerfile with several Python versions is supported.
This can be ran with `make test`. Be warned: the build will be fairly slow the first time it runs
as it installs a lot of Python versions and runs the tests against all of then.

To run tests locally, use `tox`. For more information, see
`<http://tox.readthedocs.org/en/latest/>`_.

.. code-block:: python

    pip install tox
    tox


Warning: to be able to run tests locally, Python (3.7 and 3.8) versions must be installed and in PATH.

Todo
---------

- As of now this branch is only tested with Python 3.7+ and Ansible 2.8+. With this setup all major Ansible releases (both Core and Community) should work.
- Still need to check for 2.7 and 3.5/3.6 support.
- Ansible versions lower than 2.7 are not supported: currently Suitable uses `ansible.utils.display` which was not present in 2.7 and lower.
- Mitogen is yet not supported. Still need to add tests for it.
- Tox is absurdly slow when using Docker, so all tests are being ran locally as of now. This requires Python 3.7 and 3.8 to be installed.
- Still need to make Flake8 config work with Pep8 tox command. Seems that the configuration at `setup.cfg` is not being picked up by `tox`.
- More tests are needed for multiple hosts and different hosts formats.
- Change results callback to use the new Ansible 2.8+ callback API. This would be a breaking change.
- Coverage is at about 86%. Need to test compatibility with 2.7 and Mitogen to increase significantly.
- Add stubs for `core` modules.


Build Status
------------

.. image:: https://travis-ci.org/seantis/suitable.svg?branch=master
    :target: https://travis-ci.org/seantis/suitable
    :alt: Build status

Test Coverage
-------------

.. image:: https://codecov.io/github/seantis/suitable/coverage.svg?branch=master
    :target: https://codecov.io/github/seantis/suitable?branch=master
    :alt: Test coverage

Latest Release
--------------

.. image:: https://badge.fury.io/py/suitable.svg
    :target: https://badge.fury.io/py/suitable
    :alt: Latest release
