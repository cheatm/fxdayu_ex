import logging.config
import logging


def file_initiate(config_file):
    logging.config.fileConfig(config_file)


def dict_initiate(directory=None):

    MESSAGE = " | ".join(
        ["%(asctime)s", "%(levelname)s", "%(threadName)s", "%(filename)s:%(lineno)d", "%(message)s"]
    )

    HANDLERS = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        }
    }

    if directory:
        import os
        FILE = {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "default",
            "when": "D",
            "filename": os.path.join(directory, "ExLog")
        }
        HANDLERS["file"] = FILE

    DICT_CONFIG = {
        "version": 1,
        "formatters": {
            "default": {
                "format": MESSAGE,
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "class": "logging.Formatter"
            }
        },
        "handlers": HANDLERS,
        "root": {
            "handlers": list(HANDLERS.keys()),
            "level": "DEBUG",
            "formatter": "default"
        }
    }

    logging.config.dictConfig(DICT_CONFIG)
