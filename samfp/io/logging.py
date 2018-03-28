import locale
import logging

__all__ = ['get_logger']

locale.setlocale(locale.LC_ALL, "en_US.UTF-8")


def get_logger(logger_name):

    formatter = logging.Formatter(" [%(levelname).1s %(asctime)s %(name)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(logger_name)
    logger.addHandler(handler)

    return logger


