#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
    Extract 2D Maps from Data-Cube.
"""
from __future__ import division, print_function

import argparse
import logging

__author__ = 'Bruno Quint'


class MyLogFormatter(logging.Formatter):
    err_fmt = "ERROR: %(msg)s"
    dbg_fmt = " DBG: %(module)s: %(lineno)d: %(msg)s"
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
        description='Extract 2D Maps from Fabry-Perot data-cubes.')

    parser.add_argument('data_cube', type=str, help="Cube to be cleaned.")
    parser.add_argument('-d', '--debug', action='store_true', help="Run program in debug mode.")
    parser.add_argument('-q', '--quiet', action='store_true', help="Run program quietly.")
    parser.add_argument('-s', '--show_plots', action='store_true', help="Show plots.")

    args = parser.parse_args()

    log_formatter = MyLogFormatter()
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(log_formatter)
    log = logging.getLogger()
    log.addHandler(log_handler)
    log.setLevel(logging.INFO)

    if args.debug:
        log.setLevel(logging.DEBUG)

    if args.quiet:
        log.setLevel(logging.ERROR)

    log.info('Loading %s data.' )