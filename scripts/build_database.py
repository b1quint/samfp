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
import sqlite3 as lite

from astropy.io import fits as pyfits


class DBBuilder:
    def __init__(self, _input, debug=False, verbose=True):

        self.set_verbose(verbose)
        self.set_debug(debug)

        self._input = input

        self.main(_input)

    def main(self, _input):

        self.print_header()
        files = self.get_list_of_files(_input)

    @staticmethod
    def get_files_from_directory(path):
        """
        This method delivers a list of files that are found inside the given
        'path' directory.

        Parameters
        ----------
        path : str
            The root directory that contains 'fits' images, cubes or whatever.

        Returns
        -------
        output : list
            A list of the 'fits' files found inside that path.
        """
        from os.path import join
        from glob import glob

        log.info(' Loading files within directory: {:s}'.format(path))
        output = glob(join(path, '*.fits'))

        return output

    @staticmethod
    def get_files_from_list(_list):
        """
        This method delivers a list of files that are read from an ASCII file.
        This method is called when the filename is preceeded with a '@'
        character just like IRAF.

        Parameters
        ----------
        _list : str
            The name of the ASCII file that contains a list of files to be
            read preceeded by '@'.

        Returns
        -------
        output : list
            A list of files found inside the '_list'.
        """

        log.info(' Loading files withing list: {:s}'.format(_list))
        _list = _list.replace('@', '')

        f = open(_list, 'r')
        output = f.read()
        output = output.split('\n')
        f.close()

        return output

    @staticmethod
    def get_files_from_pattern(pattern):
        """
        This method return a list of files matching the pattern. It is actually
        just a wrap for the 'glob' function with a more readable name to make
        the script consistent.

        Parameters
        ----------
        pattern : str
            The pattern that is used to find files.

        Returns
        -------
        output : list
            A list of files matching the pattern given by 'pattern'.
        """

        from glob import glob

        log.info(' Loading files matching pattern: {:s}'.format(pattern))
        output = glob(pattern)

        return output

    def get_list_of_files(self, _input):
        """

        Parameters
        ----------
        _input : str
            A string that represents the input given from the user. It can be
            a folder that will be checked out, a list of files following the
            IRAF standard (starting with '@') or a pattern that will be used
            in the Python glob.glob method.

        Returns
        -------
        output : list
            A list containing the corresponding list of images.
        """
        from os.path import isdir

        if isdir(_input):
            output = self.get_files_from_directory(_input)
        elif '@' in _input:
            output = self.get_files_from_list(_input)
        else:
            output = self.get_files_from_pattern(_input)

        return output

    @staticmethod
    def print_header():
        """
        Simply prints a message at the beginning.
        """
        msg = (
            "\n SAMI - Build Data-Base"
            " by Bruno Quint (bquint@ctio.noao.edu)"
            " 2016 - Version 0.0"
            "\n Starting program. \n")
        log.info(msg)

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
            log.debug('Setting up debug mode.')

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

    @staticmethod
    def walk(path):
        """

        Parameters
        ----------
            path : str
                Root path that will be used to look for fits files.

        Returns
        -------
            list_of_files : list
                A complete list of files
        """
        from glob import glob
        from sys import version_info

        if version_info >= (3, 5):
            log.debug('Running Python Version >= 3.5')
        else:
            log.debug('Running Python Version < 3.5')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Fix the header SAMI's ")

    parser.add_argument(
        'input',
        type=str,
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
