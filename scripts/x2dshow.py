#!/usr/bin/env python 
# -*- coding: utf8 -*-
"""
    2D Map Show

    This method is used to easily create figures from 2D maps.
"""
from __future__ import division, print_function

import datetime
import logging

import astropy.io.fits as pyfits
import matplotlib.pyplot as plt

from mpl_toolkits.axes_grid1 import make_axes_locatable

__author__ = 'Bruno C. Quint'
__date__ = '2016.11.04'
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
    log.info('\n 2D Map Show')
    log.info(' by {0}'.format(__author__))
    log.info(' Version {0} - {1}\n'.format(__version__, __date__))

    # Let's start to count the time ---
    tstart = datetime.datetime.now()
    log.debug(' [{0}] Script Start'.format(tstart.strftime('%H:%M:%S')))

    show_image(args.filename, cmap=args.colormap, show=args.show)

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
            - quiet (bool)
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
        '-c', '--colormap', default=None, type=str,
        help="Change colormap. See matplotlib.cmap documentation for syntax"
    )
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help="Enable debug mode."
    )
    parser.add_argument(
        '-q', '--quiet', action='store_true',
        help="Run program quietly. true/[FALSE]"
    )
    parser.add_argument(
        '-s', '--show', action='store_true',
        help="Show image."
    )
    args = parser.parse_args()

    return args


def show_image(filename, cmap=None, show=True):
    """
    Shows the 2D image.

    Parameters
    ----------
        filename : string
            The input filename that will be loaded and shown in the screen.
    """

    hdu = pyfits.open(filename)

    if len(hdu) == 1:
        d = hdu[0].data
        h = hdu[0].header

    if cmap is None:
        cmap = 'gray_r'

    config = {
        'cmap': cmap,
        'interpolation': 'nearest',
        'origin': 'lower'
    }

    plt.figure()
    ax = plt.gca()
    im = ax.imshow(d, **config)

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)

    plt.colorbar(im, cax=cax)

    if show:
        plt.show()


if __name__ == '__main__':
    main()