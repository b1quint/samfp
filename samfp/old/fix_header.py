#!/usr/bin/env python2
from __future__ import print_function

import argparse
import os
import logging
import signal
import sys

from astropy.io import fits as pyfits
from glob import glob
from multiprocessing import Pool

# Setting log
logging.captureWarnings(False)

log_fmt = logging.Formatter()

log_handler = logging.StreamHandler()
log_handler.setFormatter(log_fmt)

log = logging.getLogger(__name__)
log.addHandler(log_handler)
log.setLevel(logging.NOTSET)


def signal_handler(signal, frame):
    sys.exit()


def fix_header(filename):
    """
    Fix the header of images obtained with SAM and SAMI by removing the 'ADC'
    card.

    Parameters
    ----------
        filename : str
            full path that contains an FITS image.
    """

    hdu_list = pyfits.open(filename)
    signal.signal(signal.SIGINT, signal_handler)

    for hdu in hdu_list:
        try:
            del hdu.header['ADC']
        except KeyError:
            log.info('Ignoring file: %s' % filename)
            return

    log.info('Updating file: %s' % filename)
    hdu_list.writeto(filename, clobber=True)
    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Fix the header SAMI's ")
    parser.add_argument('root_dir', type=str, help="Root dir where the script "
                                                   "will walk.")
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    if args.verbose:
        log.setLevel(logging.INFO)
        log.info('Running fix_header in verbose mode ...')

    root_dir = args.root_dir
    root_dir = os.path.abspath(root_dir)
    log.info('Running fix_header inside folder: %s' % root_dir)

    list_of_files = glob(os.path.join(root_dir, '*', '*.fits'))
    list_of_files.sort()

    p = Pool(5)
    try:
        p.map_async(fix_header, list_of_files).get(99999999)
    except KeyboardInterrupt:
        log.info('\n\nYou pressed Ctrl+C!')
        log.info('Leaving now. Bye!\n')
        pass
