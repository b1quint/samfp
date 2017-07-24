#!/usr/bin/env python 
# -*- coding: utf8 -*-
"""
    2D Map Extractor

    This script is used to calculate the main 2D maps from a data-cube. All
    the maps are saved inside a single FITS file. Each maps is saved in a
    different extension.

    [0] Main extension - Contains the main header
"""
from __future__ import division, print_function

import datetime
import itertools
import logging
import os
import sys
from multiprocessing import Pool

import astropy.io.fits as pyfits
import numpy as np
from astropy.modeling import models, fitting

__author__ = 'Bruno C. Quint'
__date__ = '2016.11.03'
__version__ = '0.1'


def main():
    """
    Main function runned by the script. Do not try to import it.
    """

    # Parse arguments ---
    args = parse_arguments()

    # Load log ---
    if args.debug:
        log_level = logging.DEBUG
    elif args.quiet:
        log_level = logging.NOTSET
    else:
        log_level = logging.INFO

    log = load_log(log_level)
    log.info('\n 2D Map Plot')
    log.info(' by {0}'.format(__author__))
    log.info(' Version {0} - {1}\n'.format(__version__, __date__))

    # Let's start to count the time ---
    tstart = datetime.datetime.now()
    log.debug(' [{0}] Script Start'.format(tstart.strftime('%H:%M:%S')))

    # Now I am good. The script is already done ---
    tend = datetime.datetime.now()
    delta_t = tend - tstart

    log.debug(' [{0}] Script fineshed.'.format(tend.strftime('%H:%M:%S')))
    log.debug(' Total time elapsed: {:s}'.format(str(delta_t)))
    log.info('All done.')


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
    Receives arguments from command line and parse them. After that, returns
    a namespace to the main method.

    Returns
    -------
        args : namespace
            A namespace created by argparse containing all the configurations.
            - filename (str)
            - debug (bool)
            - pool_size (int)
            - quiet (bool)
            - output (str|None)
    """
    from argparse import ArgumentParser

    parser = ArgumentParser(
        description="This script is used to calculate the main 2D maps from a "
                    "data-cube. All the maps are saved inside a single FITS "
                    "file. Each maps is saved in a different extension."
    )
    parser.add_argument(
        'filename', type=str, help="Input data-cube name."
    )
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help="Enable debug mode."
    )
    parser.add_argument(
        '-o', '--output', default=None, type=str,
        help='Number of the output file. Each map is saved inside a different '
             'extention. If not given, a new file is created for each 2d-map.'
    )
    parser.add_argument(
        '-q', '--quiet', action='store_true',
        help="Run program quietly. true/[FALSE]"
    )
    args = parser.parse_args()

    return args


def write_results(_results, _input_file, _output_file, lorentzian=False):
    """
    Write the results to one or more FITS file.

    _results : numpy.ndarray
        A (X x Y x 3) numpy.ndarray that contains the results of the
        Gaussian fitting process performed in every pixel.
    _input_file : str
        The orginal input filename.
    _output_file : None or str
        If _output_file is a string, then all the results are stored inside a
        single FITS file with the name stored in it. Each result will be saved
        in a different extention.

        If _output_file is None, then the original name is appended with '.m*'
        and a single file is used to store each results. '.m0' contains the
        Gaussian peak value, '.m1' contains the Gaussian center and '.m2'
        contains the Gaussian stddev.
    lorentzian : bool
        Use Lorentzian instead of Gaussian
    """


if __name__ == '__main__':
    main()
