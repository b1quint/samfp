
import logging

__all__ = ['get_logger', 'SamFpLogFormatter']


def get_logger(logger_name):

    logger = logging.getLogger(logger_name)

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

    def __init__(self, fmt="%(levelno)s: %(msg)s"):
        logging.Formatter.__init__(self, fmt)

    def format(self, record):

        # Save the original format configured by the user
        # when the logger formatter was instantiated
        format_orig = self._fmt

        # Replace the original format with one customized by logging level
        if record.levelno == logging.DEBUG:
            self._fmt = SamFpLogFormatter.dbg_fmt

        elif record.levelno == logging.INFO:
            self._fmt = SamFpLogFormatter.info_fmt

        elif record.levelno == logging.ERROR:
            self._fmt = SamFpLogFormatter.err_fmt

        elif record.levelno == logging.WARNING:
            self._fmt = SamFpLogFormatter.warn_fmt

        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)

        # Restore the original format configured by the user
        self._fmt = format_orig

        return result

