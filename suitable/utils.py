from __main__ import display

import logging
import os
import typing as t
import ansible.constants

from contextlib import contextmanager
from ansible.plugins.loader import module_loader
from ansible.plugins.loader import strategy_loader

log = logging.getLogger("suitable")


VERBOSITY = {
    "critical": logging.CRITICAL,
    "error": logging.ERROR,
    "warn": logging.WARN,
    "info": logging.INFO,
    "debug": logging.DEBUG,
}


class NullHandler(logging.Handler):
    def emit(self, record):
        # type: (logging.LogRecord) -> None
        pass


def options_as_class(dictionary):
    class Options(object):
        pass

    options = Options()

    for key, value in dictionary.items():
        setattr(options, key, value)

    return options


def install_strategy_plugins(directories):
    # type: (str) -> None
    """
    Loads the given strategy plugins, which is a list of directories,
    a string with a single directory or a string with multiple directories
    separated by colon.

    As these plugins are globally loaded and cached by Ansible we do the same
    here. We could try to bind those plugins to the Api instance, but that's
    probably not something we'd ever have much of a use for.

    Call this function before using custom strategies on the :class:`Api`
    class.
    """
    if isinstance(directories, str):
        parsed_directories = directories.split(":")

    for directory in parsed_directories:
        strategy_loader.add_directory(directory)


def list_ansible_modules():
    """
    Crawls Ansible source code and returns a list of all available modules.
    Inspired by the https://github.com/ansible/ansible/blob/devel/bin/ansible-doc.

    Returns:
        set: A set of modules
    """
    modules = set()  # type: t.Set[str]
    modules_paths = module_loader._get_paths()
    paths = (p for p in modules_paths if os.path.isdir(p))
    for path in paths:
        modules.update(m for m in get_modules_from_path(path))
    return modules


def get_modules_from_path(path):
    # type: (str) -> t.Iterable[str]
    """Gets all modules from the given path.

    Args:
        path (str): The path to search for modules.

    Yields:
        Iterable: The modules found in the given path.
    """
    blacklisted_extensions = (".swp", ".bak", "~", ".rpm", ".pyc")
    blacklisted_prefixes = ("_",)
    assert os.path.isdir(path)
    subpaths = list((os.path.join(path, p), p) for p in os.listdir(path))

    for path, name in subpaths:
        if name.endswith(blacklisted_extensions):
            continue
        if name.startswith(blacklisted_prefixes):
            continue
        if os.path.isdir(path):
            for module in get_modules_from_path(path):
                yield module
        else:
            yield os.path.splitext(name)[0]


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
    """Temporarily overrides an environment variable."""

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
    """Temporarily disables host_key_checking, which is set globally."""

    def as_string(b):
        return b and "True" or "False"

    with environment_variable("ANSIBLE_HOST_KEY_CHECKING", as_string(enable)):
        previous = ansible.constants.HOST_KEY_CHECKING
        ansible.constants.HOST_KEY_CHECKING = enable
        yield
        ansible.constants.HOST_KEY_CHECKING = previous


log.addHandler(NullHandler())
