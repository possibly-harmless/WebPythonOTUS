import logging
import os.path

DEFAULT_LOG_PATH = None
DEFAULT_LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
if not os.path.exists(DEFAULT_LOG_DIR):
    try:
        os.mkdir(DEFAULT_LOG_DIR)
    except OSError:
        DEFAULT_LOG_DIR = None
if  DEFAULT_LOG_DIR:
    DEFAULT_LOG_PATH = os.path.join(DEFAULT_LOG_DIR, "search.log")

class SearchLogger:

    _instance = None

    @classmethod
    def get_logger(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = cls(*args, **kwargs)
        return cls._instance

    def __init__(self, path=DEFAULT_LOG_PATH, log_to_console=True, level="info"):
        log_level = {
            "info": logging.INFO,
            "error":logging.ERROR,
            "warning": logging.WARNING,
            "debug": logging.DEBUG
        }.get(level, logging.INFO)

        handlers = []
        if path:
            handlers.append(logging.FileHandler(path, mode='w'))
        if log_to_console or not path:
            handlers.append(logging.StreamHandler())

        logging.root.handlers = []
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=handlers
        )

    def info(self, msg):
        return logging.info(msg)

    def error(self, msg):
        return logging.error(msg)

    def warning(self, msg):
        return logging.warning(msg)

    def debug(self, msg):
        return logging.debug(msg)


