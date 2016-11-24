#!/usr/bin/env python 
# -*- coding: utf8 -*-
"""
    2D Map Show

    This method is used to easily create figures from 2D maps.
"""
from __future__ import division, print_function

import datetime
import logging
import matplotlib.pyplot as plt

from astropy.io import fits as pyfits
from astropy.visualization import PercentileInterval
from astropy.visualization import LinearStretch
from astropy.visualization.mpl_normalize import ImageNormalize
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

    show_image(
        args.filename, cmap=args.colormap, show=args.show, title=args.title
    )

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
        help="Change colormap. See http://matplotlib.org/users/colormaps.html "
             "for more."
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
    parser.add_argument(
        '-t', '--title', default=None, type=str,
        help="Set image title."
    )
    args = parser.parse_args()

    return args


def show_image(filename, cmap=None, show=True, title=None):
    """
    Shows the 2D image.

    Parameters
    ----------
        filename : string
            The input filename that will be loaded and shown in the screen.
        cmap : string / None
            The colormap that will be used. Please refer to the link [1]
            for more info. If None, grey map will be used.
        show : bool
            Show the plot?
        title : string / None
            The image title.

    [1] http://matplotlib.org/users/colormaps.html
    """

    hdu = pyfits.open(filename)

    if len(hdu) == 1:
        d = hdu[0].data
        h = hdu[0].header

    if cmap is None:
        cmap = 'gray_r'

    if 'units' in h:
        units = h['units']
    else:
        units = '--'

    if title is None:
        title = ''

    norm = ImageNormalize(
        stretch=LinearStretch()
    )

    config = {
        'cmap': cmap,
        'interpolation': 'nearest',
        'norm': norm,
        'origin': 'lower'
    }

    fig = plt.figure()

    ax = plt.gca()
    im = ax.imshow(d, **config)

    ax.grid()
    ax.set_title(title)

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)

    cbar = plt.colorbar(im, cax=cax)
    cbar.set_label('[{:s}]'.format(units))

    fig.tight_layout()

    if show:
        plt.show()


if __name__ == '__main__':
    main()