import logging
import os
import sys
from builtins import input

__all__ = ['input', 'safe_save', 'MyLogFormatter']


def safe_save(name, extension=None, overwrite=False, verbose=False):
    """
    This is a generic method used to check if a file called 'name' already
    exists. If so, it starts some interaction with the user.

    @param name: the name of the file that will be written in the future.

    @keyword extension: check if the file has the following extension. If not,
    it fills for the user. Defaults is None. An example would be
    extension='.fits'.

    @keyword overwrite: if False, this method will interact with the user to
    ask if 'name' file shall be overwritten or if a new name will be given. If
    True, 'name' file is automatically overwritten.

    @keyword verbose: force verbose mode on even when overwrite is automatic.

    v1.0.2 - added 'extension' keyword.
    v1.0.1 - added 'overwrite' keyword.
           - added 'verbose' keyword.
    """
    log = logging.getLogger()

    if os.path.splitext(name)[1] != extension and extension is not None:
        name = name + extension

    v = False if (overwrite is True) else True
    if v:
        log.info('\nWriting to output file "%s"' % name)

    while os.path.exists(name):

        if overwrite in ['y', 'Y', True]:
            if v or verbose:
                log.info(" Overwriting %s file." % name)
            os.remove(name)

        elif overwrite in ['', 'n', 'N', False]:
            name = input("Please, enter a new filename:\n > ")
            if os.path.splitext(name)[1] != extension and extension is not None:
                name = name + extension

        elif overwrite in ['q']:
            if v:
                log.info("Exiting program.")
            sys.exit()

        else:
            overwrite = input(" '%s' file exist. Overwrite? (y/[n])" % name)
            if v:
                log.info("Writing data-cube to %s" % name)

    return name


# class MyLogFormatter(logging.Formatter):
#
#     err_fmt = "E %(msg)s"
#     dbg_fmt = "D %(module)s: %(lineno)d: %(msg)s"
#     info_fmt = "I %(msg)s"
#     warn_fmt = "W %(msg)s"
#
#     def __init__(self, fmt="%(levelno)s: %(msg)s"):
#         logging.Formatter.__init__(self, fmt)
#
#     def format(self, record):
#
#         # Save the original format configured by the user
#         # when the logger formatter was instantiated
#         format_orig = self._fmt
#
#         # Replace the original format with one customized by logging level
#         if record.levelno == logging.DEBUG:
#             self._fmt = MyLogFormatter.dbg_fmt
#
#         elif record.levelno == logging.INFO:
#             self._fmt = MyLogFormatter.info_fmt
#
#         elif record.levelno == logging.ERROR:
#             self._fmt = MyLogFormatter.err_fmt
#
#         elif record.levelno == logging.WARNING:
#             self._fmt = MyLogFormatter.warn_fmt
#
#         # Call the original formatter class to do the grunt work
#         result = logging.Formatter.format(self, record)
#
#         # Restore the original format configured by the user
#         self._fmt = format_orig
#
#         return result
