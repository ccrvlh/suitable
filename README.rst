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

* Python 2.7 and Python 3.5+.
* Ansible 2.4+
* Mitogen 0.2.6+ (currently incompatible with Ansible 2.8)

Support for older releases is kept only if possible. New Ansible releases
are favored over old ones.

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


Warning: to be able to run tests locally all Python versions must be installed and in PATH.


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
