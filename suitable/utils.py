import logging


def options_as_class(dictionary):

    class Options(object):
        pass

    options = Options()

    for key, value in dictionary.items():
        setattr(options, key, value)

    return options

LOG_VERBOSITY = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warn': logging.WARN,
    'info': logging.INFO,
    'debug': logging.DEBUG
}

