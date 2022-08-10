import logging
log = logging.getLogger('suitable')


class NullHandler(logging.Handler):
    def emit(self, record):
        # type: (logging.LogRecord) -> None        
        pass


log.addHandler(NullHandler())
