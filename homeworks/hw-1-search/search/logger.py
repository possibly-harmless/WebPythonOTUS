import logging
import os.path

DEFAULT_LOG_PATH = None
DEFAULT_LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
if not os.path.exists(DEFAULT_LOG_DIR):
    try:
        os.mkdir(DEFAULT_LOG_DIR)
    except OSError:
        DEFAULT_LOG_DIR = None
if DEFAULT_LOG_DIR:
    DEFAULT_LOG_PATH = os.path.join(DEFAULT_LOG_DIR, "search.log")


def with_logging_methods(methods):
    """
    Class decorator to add logging methods like info(), warning(), ... to logger class
    :param methods: A list of string method names
    :return: Class decorator
    """
    def logger_decorator(clazz):
        def create_log_method(name):
            def inner(self, msg, force_console_print=False):
                if logging.root.isEnabledFor(self.log_level_mappings()[name]):
                    getattr(logging, name)(msg)
                elif force_console_print:
                    print(msg)
            return inner

        for level in methods:
            setattr(clazz, level, create_log_method(level))

        return clazz
    return logger_decorator


@with_logging_methods(("info", "error", "warning", "debug", "critical"))
class SearchLogger:

    _instance = None

    @classmethod
    def get_logger(cls):
        if not cls._instance:
            raise RuntimeError(
                "Logger should be initialized before the first use. Use SearchLogger.init_logger() to do so."
            )
        return cls._instance

    @classmethod
    def init_logger(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = cls(*args, **kwargs)

    @classmethod
    def log_level_mappings(cls):
        return {
            "info": logging.INFO,
            "error": logging.ERROR,
            "warning": logging.WARNING,
            "debug": logging.DEBUG,
            "critical": logging.CRITICAL
        }

    @classmethod
    def get_actual_log_level(cls, level):
        return cls.log_level_mappings().get(level, logging.INFO)

    def __init__(self, path=DEFAULT_LOG_PATH, log_to_console=True, level="info"):
        log_level = self.__class__.get_actual_log_level(level)
        handlers = []
        if path:
            handlers.append(logging.FileHandler(path, mode='w'))
        if log_to_console or not path:
            handlers.append(logging.StreamHandler())
        logging.root.handlers = []
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=handlers
        )
