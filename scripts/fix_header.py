#!/usr/bin/env python2
from __future__ import print_function

import argparse
import os
import logging

from astropy.io import fits as pyfits
from glob import glob
from multiprocessing import Pool

# Setting log
logging.captureWarnings(True)

log_fmt = logging.Formatter()

log_handler = logging.FileHandler('log.fix_header')
log_handler.setFormatter(log_fmt)

log = logging.getLogger(__name__)
log.addHandler(log_handler)
log.setLevel(logging.DEBUG)


def fix_header(filename):
    """
    Fix the header of images obtained with SAM and SAMI by removing the 'ADC'
    card.

    Parameters
    ----------
        filename : str
            full path that contains an FITS image.
    """
    log.debug(filename)
    hdu_list = pyfits.open(filename)

    for hdu in hdu_list:
        try:
            del hdu.header['ADC']
        except KeyError:
            return

    hdu_list.writeto(filename, clobber=True)
    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Fix the header SAMI's ")
    parser.add_argument('root_dir', type=str, help="Root dir where the script "
                                                   "will walk.")
    args = parser.parse_args()

    root_dir = args.root_dir
    root_dir = os.path.abspath(root_dir)
    log.info('Running fix_header inside folder: %s' % root_dir)

    list_of_files = glob(os.path.join(root_dir, '*', '*.fits'))
    list_of_files.sort()

    p = Pool(5)
    p.map(fix_header, list_of_files)