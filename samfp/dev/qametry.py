#!/usr/bin/env python 
# -*- coding: utf8 -*-
"""
    Quick Astrometry

    By Bruno Quint
    bquint at ctio.noao.edu
"""
from __future__ import division, print_function

import datetime
import logging

import astropy.io.fits as pyfits
import numpy as np

from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy.stats import sigma_clipped_stats
from astropy import wcs
from photutils import daofind

import matplotlib.pyplot as plt
from astropy.visualization import SqrtStretch
from astropy.visualization.mpl_normalize import ImageNormalize
from photutils import CircularAperture

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
    log.info('\n SAMI QAstroMetry')
    log.info(' by {0}'.format(__author__))
    log.info(' Version {0} - {1}\n'.format(__version__, __date__))

    # Let's start to count the time ---
    tstart = datetime.datetime.now()
    log.debug(' [{0}] Script Start'.format(tstart.strftime('%H:%M:%S')))

    # For each file, run
    for f in args.filenames:

        log.info('\n Load data: {:s}'.format(f))
        data = pyfits.getdata(f)
        h = pyfits.getheader(f)

        if h['NAXIS'] == 3:
            d = np.sum(data, axis=0)

        mean, median, std = sigma_clipped_stats(d, sigma=3.0, iters=5)
        sources = daofind(d, fwhm = 3.0, threshold = 5. * std)

        positions = (sources['xcentroid'], sources['ycentroid'])
        apertures = CircularAperture(positions, r=4.)
        norm = ImageNormalize(stretch=SqrtStretch())
        plt.imshow(d, cmap='Greys', origin='lower', norm=norm)
        apertures.plot(color='blue', lw=1.5, alpha=0.5)
        # plt.show()

        #c = SkyCoord(h['RA'] + h['DEC'], unit=(u.hourangle, u.deg))
        #theta = np.radians(h['DECPANGL'])
        #delta = 1.2639E-5

        # Create a new WCS object.  The number of axes must be set
        # from the start
        # w = wcs.WCS(naxis=2)

        # Set up an "Airy's zenithal" projection
        # Vector properties may be set with Python lists, or Numpy arrays
        # w.wcs.crpix = [d.shape[1] // 2, d.shape[0]]
        # w.wcs.cdelt = np.array([delta * np.cos(theta), delta * np.cos(theta)])
        # w.wcs.crval = [c.ra.deg, c.dec.deg]
        # w.wcs.ctype = ["RA---DEG", "DEC--DEG"]

        h.add_history('Quick astrometry made using coordinates and PA.')

        #pyfits.writeto(f.replace('.fits', '.qa.fits'), data, h, clobber=True)

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
            - filenames (list)
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
        '-d', '--debug', action='store_true',
        help="Enable debug mode."
    )
    parser.add_argument(
        'filenames', nargs='+', type=str, help="Fits name(s)."
    )
    parser.add_argument(
        '-q', '--quiet', action='store_true',
        help="Run program quietly. true/[FALSE]"
    )
    args = parser.parse_args()

    return args

if __name__ == '__main__':
    main()
