#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
    Build SAMI Data-Base

    This script receives a path, a list of files or a file
    containing a list of files. Then, it walks through them
    and create a data-base with several information that can
    be read in other ways.

    by Bruno C. Quint
    SOAR Telescope - 2016.10.01
"""

import argparse
import logging as log


class DBBuilder:
    def __init__(self, _input, debug=False, verbose=True):

        self.set_verbose(verbose)
        self.set_debug(debug)

        self._input = input

    @staticmethod
    def set_debug(debug):
        """
        Turn on debug mode.

        Parameter
        ---------
            debug : bool
        """
        if debug:
            log.basicConfig(level=log.DEBUG, format='%(message)s')

    @staticmethod
    def set_verbose(verbose):
        """
        Turn on verbose mode.

        Parameter
        ---------
            verbose : bool
        """
        if verbose:
            log.basicConfig(level=log.INFO, format='%(message)s')
        else:
            log.basicConfig(level=log.WARNING, format='%(message)s')

    @staticmethod
    def get_files(_input):

        log.debug()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Fix the header SAMI's ")

    parser.add_argument(
        'input',
        type=list, nargs='+',
        help="This file can be a list of input files, a path to a folder "
             "containing files or to a text file containing the files to be "
             "imported (start it with '@')."
    )

    parser.add_argument(
        '-D', '--debug',
        action='store_true',
        help="Turn on DEBUG mode (overwrite quiet mode)."
    )

    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help="Run the script without printing anything."
    )

    args = parser.parse_args()

    DBBuilder(args.input, debug=args.debug, verbose=not args.quiet)
