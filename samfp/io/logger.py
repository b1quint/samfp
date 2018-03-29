#!/usr/bin/env python
# -*- coding: utf8 -*-

import logging
import sys

__all__ = ['COLORS', 'get_logger']

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

RESET_SEQ = '\033[0m'
COLOR_SEQ = '\033[1;%dm'
BOLD_SEQ = '\033[1m'

COLORS = {
    'WARNING': YELLOW,
    'INFO': WHITE,
    'DEBUG': BLUE,
    'CRITICAL': RED,
    'ERROR': RED
}


def get_logger(logger_name, use_color=True):
    """
    Return a logger with the "logger_name".

    Args:
        logger_name (str) : the logger name to be used in different contexts.
        use_colors (bool, optional) : use colors on Stream Loggers.

    Returns:
        _logger (logging.Logger) : the logger to be used.
    """
    message_format = " [%(levelname).1s %(asctime)s %(name)s] %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    formatter = SamFpLogFormatter(message_format, datefmt=date_format, use_colours=use_color)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logging.setLoggerClass(SamFpLogger)
    _logger = logging.getLogger(logger_name)
    _logger.addHandler(handler)
    _logger.setLevel(logging.DEBUG)

    return _logger


class SamFpLogFormatter(logging.Formatter):

    def __init__(self, fmt="%(levelno)s: %(msg)s", datefmt=None, use_colours=True):
        logging.Formatter.__init__(self, fmt, datefmt=datefmt)
        self.use_colours = use_colours

    @staticmethod
    def color_format(message, levelname, left_char="[", right_char="]"):

        colour = COLOR_SEQ % (30 + COLORS[levelname])

        message = message.replace(left_char, "{:s} {:s}".format(colour, left_char))
        message = message.replace(right_char, "{:s} {:s}".format(right_char, RESET_SEQ))

        return message

    def format(self, record):

        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)

        if self.use_colours:
            result = self.color_format(result, record.levelname)

        return result


class SamFpLogger(logging.Logger):

    def __init__(self, name, verbose=True, debug=False):
        logging.Logger.__init__(self, name)
        self.set_verbose(verbose)
        self.set_debug(debug)

    def set_verbose(self, verbose=True):
        if verbose:
            self.setLevel(logging.INFO)
        else:
            self.setLevel(logging.NOTSET)

    def set_debug(self, debug=True):
        if debug:
            self.setLevel(logging.DEBUG)


if __name__ == "__main__":

    logger = get_logger('TestColor')
    logger.setLevel(logging.DEBUG)

    logger.debug("debug message")
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")
    logger.critical("critical message")
