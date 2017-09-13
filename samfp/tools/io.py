from builtins import input

import logging
import os
import sys

__all__ = ['input', 'safe_save', 'MyLogFormatter']


def safe_save(name, extension=None, overwrite=False, verbose=False):
    """
        This is a generic method used to check if a file called 'name'
        already exists. If so, it starts some interaction with the user.

        Parameters:
            name : str
                The name of the file that will be written in the future.

            extension: str (default=None)
                Check if the file has the following extension. If not, it fills
                for the user. Defaults is None. An example would be
                extension='.fits'.

            overwrite : bool
                If False, this method will interact with the user to ask if 'name'
                file shall be overwritten or if a new name will be given. If True,
                'name' file is automatically overwritten.

            verbose : bool
                force verbose mode on even when overwrite is automatic.
    """

    log = MyLogger(__name__)
    log.set_verbose(verbose=verbose)

    if os.path.splitext(name)[1] != extension and extension is not None:
        name = name + extension

    log.info('Writing to output file "%s"' % name)

    while os.path.exists(name):

        if overwrite in ['y', 'Y', True]:
            log.info("Overwriting %s file." % name)
            os.remove(name)

        elif overwrite in ['', 'n', 'N', False]:
            name = input("    Please, enter a new filename:\n    > ")
            if os.path.splitext(name)[1] != extension and extension is not None:
                name = name + extension

        elif overwrite in ['q']:
            log.info("Exiting program.")
            sys.exit()

        else:
            overwrite = input(" '%s' file exist. Overwrite? (y/[n])" % name)
            log.info('Writing to output file "%s"' % name)

    return name


class MyLogFormatter(logging.Formatter):

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
            self._fmt = MyLogFormatter.dbg_fmt

        elif record.levelno == logging.INFO:
            self._fmt = MyLogFormatter.info_fmt

        elif record.levelno == logging.ERROR:
            self._fmt = MyLogFormatter.err_fmt

        elif record.levelno == logging.WARNING:
            self._fmt = MyLogFormatter.warn_fmt

        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)

        # Restore the original format configured by the user
        self._fmt = format_orig

        return result


class MyLogger(logging.Logger):

    def __init__(self, name, verbose=True, debug=False):
        logging.Logger.__init__(self, name)

        # Set log format
        self.formatter = MyLogFormatter()

        # Set log handler to the terminal
        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setFormatter(self.formatter)

        # Set the logger itself
        self.addHandler(self.stream_handler)

    def set_verbose(self, verbose=True):
        if verbose:
            self.setLevel(logging.INFO)
        else:
            self.setLevel(logging.NOTSET)

    def set_debug(self, debug=True):
        if debug:
            self.setLevel(logging.DEBUG)
