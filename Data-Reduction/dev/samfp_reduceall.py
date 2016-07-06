#/usr/bin/env python
# -*- coding: utf8 -*-

from __future__ import division, print_function

import argparse
import logging

__author__ = 'Bruno Quint'


class SAMFP(object):
    """
    Script that fully reduces SAMFP data. All the data have to be inside the
    **root_folder** that is given as argument to the class constructor.
    """
    def __init__(self, root_folder, log=None):
        """
        Start a SAM-FP pipeline for data reduction.
        :param root_folder: the path that holds all the data.
        :param log:
        """

        if (log is not None) or (isinstance(log, logging.Logger)):
            raise TypeError('Log should be an **logging.Logger** object.')

        self.log = self.get_logger() if log is None else log
        self.root = root_folder

    def start(self):
        """
        Start the pipeline with some interaction with the user.
        :return:
        """
        # Check if reduced folder exists ---
        ## if exists, check what is done
        ## if not, create it and do everything

        # Check if local database exists ---
        ## If yes, open it
        ## If not, create a new one

        # Group files according to the observing type:
        # [BIAS, DARK, FLAT, COMP, OBJECT]
        # ignore all files that has one of the following COMMENTS
        # [acquisition, acq, focus, dummy]

        # Combine all image's extensions and save them into the reduced folder

        # Combine BIAS into master_bias
        # Subtract master_bias from all other files

        # Combine DARK into master_dark
        # Subtract master_dark from all other files to remove glow

        #



class MyLogFormatter(logging.Formatter):

    err_fmt  = "ERROR: %(msg)s"
    dbg_fmt  = " DBG: %(module)s: %(lineno)d: %(msg)s"
    info_fmt = " %(msg)s"
    warn_fmt = " %(msg)s"

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


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Full pipeline to reduce SAM-FP data.")

    parser.add_argument('root_folder', type=str,
        help="Root folder that contains all the data.")
    parser.add_argument('-d', '--debug', action='store_true',
        help="Run program in debug mode.")
    parser.add_argument('-q', '--quiet', action='store_true',
        help="Run program quietly.")
    parser.add_argument('-s', '--show_plots', action='store_true',
        help="Show plots.")

    args = parser.parse_args()

    log_formatter = MyLogFormatter()
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(log_formatter)
    log = logging.getLogger()
    log.addHandler(log_handler)

    samfp = SAMFP(log)
    samfp.start()
