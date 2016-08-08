#!/usr/bin/env python 
# -*- coding: utf8 -*-
"""
    Split Scan Files

    This script splits the scan files based on their header informations. This
    makes easier to handle the data later.
"""
from __future__ import division, print_function
from multiprocessing import Pool

import argparse
import astropy.io.fits as pyfits
import glob
import logging
import pandas as pd
import sys

__author__ = 'Bruno Quint'
__version__ = '0.0.0'
__date__ = '2016.08.09'


def main():

    # Parse Arguments ---
    args = parse_arguments()

    files = []
    for f in args.files:
        for ff in glob.glob(f):
            files.append(ff)

    # Load log ---
    if args.debug:
        log_level = logging.DEBUG
    elif args.quiet:
        log_level = logging.NOTSET
    else:
        log_level = logging.INFO

    log = load_log(log_level)
    log.info('\n Split SAM-FP Files')
    log.info(' by {0}'.format(__author__))
    log.info(' Version {0} - {1}\n'.format(__version__, __date__))

    # Create Data-Frame --------------------------------------------------------
    names = [
        'FILENAME',
        'OBSTYPE',
        'OBJECT',
        'COMMENT',
        'DATE-OBS',
        'TIME-OBS',
        'FAPERSID',
        'FAPERSWP',
        'FAPERSST',
        'FAPEROTZ'
    ]

    try:
        df = pd.read_csv(args.table, names=names)
    except:
        df = pd.DataFrame(columns=names)

    # Feed Data-Frame ----------------------------------------------------------
    frame_feeded = DF_Feeder(df)
    p = Pool(4)
    try:
        series = p.map_async(frame_feeded, files).get(99999999)
    except KeyboardInterrupt:
        log.info('\n\nYou pressed Ctrl+C!')
        log.info('Leaving now. Bye!\n')
        pass

    df = df.append(series)
    df['COMMENT'] = df['COMMENT'].apply(clear_comments)

    # Create Folders -----------------------------------------------------------
    # Move files ---------------------------------------------------------------
    # Save data-frame ----------------------------------------------------------
    df.to_csv(args.table)
    # Exit ---


def clear_comments(my_header_comment):
    """
    Clear the COMMENT column in the data-frame.

    Parameters
    ----------
        my_header_comment : astropy.io.fits.header._HeaderCommentaryCards

    Returns
    -------
        my_string : str
            The COMMENT value without all the comments in the header.
    """
    try:
        my_string = my_header_comment[4]
        my_string = my_string.replace('=', '').split('/')[0]
        return my_string
    except (IndexError, TypeError):
        my_header_comment


def load_log(level):
    """
    Load a log that controls the amount of information that is shown to the
    user.

    Parameter
    ---------
        level : logging.Level

    Return
    ------
        log : logging.log
    """

    logging.captureWarnings(False)

    formatter = logging.Formatter()

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    log = logging.getLogger(__name__)
    log.addHandler(handler)
    log.setLevel(level)

    return log


def parse_arguments():
    """
    Parse the arguments providen in the command line.
    """

    parser = argparse.ArgumentParser(
        description="This script split the files into different folders"
                    "deppending on their observation type, object name and "
                    "starting time"
    )
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help="Enable debug mode."
    )
    parser.add_argument(
        'files', type=str, nargs='+',
        help="Files that have to be splitted."
    )
    parser.add_argument(
        '-q', '--quiet', action='store_true',
        help="Run program quietly. true/[FALSE]"
    )
    parser.add_argument(
        '-t', '--table', type=str, default='my_table.csv',
        help='CSV file that contains/will contain the table.'
    )
    args = parser.parse_args()

    return args


def signal_handler(signal, frame):
    sys.exit()


class DF_Feeder:
    """
    Data-Frame feeder. This class is simply a workaround to make the proccess
    of reading the FITS files faster.
    """
    def __init__(self, data_frame):
        """
        Parameters
        ----------
            data_frame : pandas.DataFrame
                A data-frame containing the following column names:
                [...]
        """
        self.df = data_frame

    def __call__(self, filename):
        """
        Parameter
        ---------
            filename : str
                A string that contains the path to the filename that will be
                read.
        """
        keys = self.df.keys()

        try:
            header = pyfits.getheader(filename)
            info = [header[k] for k in keys]
        except IOError:
            info = [None for k in keys]

        s = pd.Series(info, index=keys, name=filename)
        return s

if __name__ == '__main__':
    main()