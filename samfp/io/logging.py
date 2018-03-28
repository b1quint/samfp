
import logging

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

#These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

COLORS = {
    'WARNING': YELLOW,
    'INFO': WHITE,
    'DEBUG': BLUE,
    'CRITICAL': YELLOW,
    'ERROR': RED
}


def get_logger(logger_name, use_color=True):
    """
    Return a logger with the "logger_name".

    Parameters
    ----------
        logger_name (str) : the logger name to be used in different contexts.
        use_colors (bool, optional) : use colors on Stream Loggers.

    Return
    ------
        logger (logging.Logger) : the logger to be used.
    """
    message_format = " [%(levelname).1s %(asctime)s %(name)s] %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    formatter = SamFpLogFormatter(message_format, datefmt=date_format)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(logger_name)
    logger.addHandler(handler)

    return logger


class SamFpLogFormatter(logging.Formatter):

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    err_fmt = FAIL + "[E]" + ENDC + " %(msg)s"
    dbg_fmt = OKBLUE + "[D]" + ENDC + " %(module)s: %(lineno)d: %(msg)s"
    info_fmt = "    %(msg)s"
    warn_fmt = WARNING + "[!]" + ENDC + " %(msg)s"

    def __init__(self, fmt="%(levelno)s: %(msg)s", datefmt=None, use_colours=True):
        logging.Formatter.__init__(self, fmt, datefmt=datefmt)
        self.use_colours = use_colours

    def color_format(self, fmt, levelname, left_char="[", right_char="]"):

        color = COLOR_SEQ % (30 + COLORS[levelname])

        fmt = fmt.replace(left_char, "{:s}{:s}".format(COLOR_SEQ, left_char))
        fmt = fmt.replace(left_char, "{:s}{:s}".format(right_char, RESET_SEQ))

        return fmt

    def format(self, record):

        format_orig = self._fmt

        if self.use_colours:
                self._fmt = self.color_format(self._fmt, record.levelname)

        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)

        # Restore the original format configured by the user
        self._fmt = format_orig

        return result
