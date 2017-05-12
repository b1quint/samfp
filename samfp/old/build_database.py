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

import argparse as _argparse
import glob as _glob
import logging as log
import os.path
import pandas as _pd
import sqlite3 as _sqlite3

from astropy.io import fits as _pyfits
from samfp.globals import csv_columns

class DBBuilder:
    def __init__(self, _input, debug=False, verbose=True):

        self.set_verbose(verbose)
        self.set_debug(debug)
        self._input = input

        self.main(_input)

    def main(self, _input):

        self.print_header()
        files = self.get_list_of_files(_input)
        self.build_database(files)

    @staticmethod
    def build_database(files, database='temp.csv'):
        """
        Let us finally build a data-base to store all the images and their
        informations.

        Parameters
        ----------
        files : list
            List of files that will be added to the data-base
        database : str
            The name of the file that will store the database information.
            By default, this is set to 'temp.csv'
        """
        files.sort()

        df = _pd.DataFrame(columns=csv_columns)
        for i in range(len(files)):
            p, f = os.path.split(files[i])
            f = f if '.fits' in f else f + '.fits'
            absfilename = os.path.abspath(os.path.join(p, f))
            h = _pyfits.getheader(absfilename)
            h['FILENAME'] = absfilename
            if 'NEXTEND' not in h:
                log.warning(
                    ' {:s} was not found in file {:s}'.format(
                        'NEXTEND', files[i]
                    )
                )
                h.set('NEXTEND', '1')
            df.loc[i] = [h[c] for c in csv_columns]

        df.to_csv(database)


    @staticmethod
    def get_files_from_directory(path, recursive=True):
        """
        This method delivers a list of files that are found inside the given
        'path' directory.

        Parameters
        ----------
        path : str
            The root directory that contains 'fits' images, cubes or whatever.
        recursive : bool
            If True, this method looks one folder deeper for fits files.

        Returns
        -------
        output : list
            A list of the 'fits' files found inside that path.
        """
        log.info(' Loading files within directory: {:s}'.format(path))
        
        output = _glob.glob(os.path.join(path, '*.fits'))
        output += _glob.glob(os.path.join(path, '*.fits.bz2'))
        output += _glob.glob(os.path.join(path, '**', '*.fits'))
        output += _glob.glob(os.path.join(path, '**', '*.fits.bz2'))

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
        log.info(' Loading files matching pattern: {:s}'.format(pattern))
        output = _glob.glob(pattern)

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
        if os.path.isdir(_input):
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
            log.getLogger().setLevel(log.DEBUG)
            log.debug('Setting debug mode.')

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


if __name__ == '__main__':
    parser = _argparse.ArgumentParser(description="Fix the header SAMI's ")

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

    parser.add_argument(
        '-o', '--output',
        type=str, default='table.csv',
        help='Name of the output CSV file.'
    )

    args = parser.parse_args()

    DBBuilder(args.input, debug=args.debug, verbose=not args.quiet)
