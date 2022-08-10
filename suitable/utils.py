import logging
import os
import typing as t

from ansible.plugins.loader import module_loader
from ansible.plugins.loader import strategy_loader

log = logging.getLogger('suitable')

VERBOSITY = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warn': logging.WARN,
    'info': logging.INFO,
    'debug': logging.DEBUG
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
        parsed_directories = directories.split(':')

    for directory in parsed_directories:
        strategy_loader.add_directory(directory)


def list_ansible_modules():
    """
    Crawls Ansible source code and returns a list of all available modules.
    Inspired by the https://github.com/ansible/ansible/blob/devel/bin/ansible-doc.

    Returns:
        set: A set of modules
    """    
    modules = set()
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
    blacklisted_extensions = ('.swp', '.bak', '~', '.rpm', '.pyc')
    blacklisted_prefixes = ('_', )
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


log.addHandler(NullHandler())
