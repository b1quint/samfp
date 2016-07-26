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

import astropy.io.fits as pyfits
import itertools
import logging
import numpy as np
import signal
import sys
import warnings

from astropy.modeling import models, fitting
from multiprocessing import Pool

__author__ = 'Bruno Quint'


def signal_handler(signal, frame):
    sys.exit()


def main():

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

    # Load data ---
    data = pyfits.getdata(args.filename)
    header = pyfits.getheader(args.filename)

    log.debug('Estimate spectral continuum using median.')
    continuum = np.median(data, axis=0)
    header.add_history('Spectral continuum estimated using median.')
    pyfits.writeto(
        args.filename.replace('.wcal', '.cont'),
        continuum, header=header, clobber=True
    )

    z = np.arange(data.shape[0])
    z = (z - header['CRPIX3'] + 1) * header['CDELT3'] + header['CRVAL3']

    # p = data / np.sum(data, axis=0)
    #
    # e1 = (z * p).sum(axis=0)
    # e2 = (((z - e1) ** 2 * p).sum(axis=0) ** (1 / 2))
    # e3 = (((z - e1) ** 3 * p).sum(axis=0) ** (1 / 3))
    # e4 = (((z - e1) ** 4 * p).sum(axis=0) ** (1 / 4))
    #
    # e = [e1, e2, e3, e4]
    # for i in range(4):
    #     pyfits.writeto(args.filename.replace('.wcal', '.m{:d}'.format(i + 1)),
    #                    e[i], header=header, clobber=True)

    m = np.zeros_like(data[0])
    fitter = fitting.LevMarLSQFitter()
    for (j, i) in itertools.product(range(data.shape[1]), range(data.shape[2])):
        signal = data[:, j, i]
        g_init = models.Gaussian1D(amplitude=signal.max(), mean=z[signal.argmax()], stddev=1.0)
        g_fit = fitter(g_init, z, signal)
        m[j, i] = g_fit.amplitude.value

    log.debug('All done.')


def clean_header(header):
    # TODO Docstring

    try:
        for key in ['NEXTEND', 'PREFLASH', 'ADC', 'CRPIX3', 'CRVAL3', 'CDELT3',
                    'C3_3', 'CR3_3', 'CUNITS3']:
            del header[key]
    except:
        pass

    return header


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
    """
    from argparse import ArgumentParser

    parser = ArgumentParser(
        description="This script is used to calculate the main 2D maps from a "
                    "data-cube. All the maps are saved inside a single FITS "
                    "file. Each maps is saved in a different extension."
    )
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help="Enable debug mode."
    )
    parser.add_argument(
        'filename', type=str, help="Input data-cube name."
    )
    parser.add_argument(
        '-o', '--output', type=str, default=None,
        help="Name of the output phase-map file."
    )
    parser.add_argument(
        '-q', '--quiet', action='store_true',
        help="Run program quietly. true/[FALSE]"
    )
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    main()