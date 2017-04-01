#!/usr/bin/env python 
# -*- coding: utf8 -*-
from __future__ import division, print_function

from scipy.stats import mode

__author__ = 'Bruno Quint'


class FlatCombine:

    def __init__(self, verbose=False, debug=False):
        import logging as log
        self._log = log
        self.set_verbose(verbose)
        self.set_debug(debug)
        return

    def debug(self, message):
        """Print a debug message using the logging system."""
        self._log.debug(message)

    def info(self, message):
        """Print an info message using the logging system."""
        self._log.info(message)

    def mode(self, data):
        temp = mode(data[200:-200, 200:-200].rave())[0]
        return temp

    def set_debug(self, debug):
        """
        Turn on debug mode.

        Parameter
        ---------
            debug : bool
        """
        if debug:
            self._log.basicConfig(level=self._log.DEBUG, format='%(message)s')

    def set_verbose(self, verbose):
        """
        Turn on verbose mode.

        Parameter
        ---------
            verbose : bool
        """
        if verbose:
            self._log.basicConfig(level=self._log.INFO, format='%(message)s')
        else:
            self._log.basicConfig(level=self._log.WARNING, format='%(message)s')

    def warn(self, message):
        """Print a warning message using the logging system."""
        self._log.warning(message)

    def run(self, input_files, output_file='o.fits'):

        import numpy as np

        from astropy.io import fits as pyfits
        from astropy import units as u
        from ccdproc import CCDData, combine
        from scipy import stats

        list_of_data = []
        for f in input_files:

            hdr = pyfits.getheader(f)
            data = pyfits.getdata(f)
            data = CCDData(data, unit=u.adu)
            list_of_data.append(data)

        master_flat = combine(list_of_data, method='median',
                              mem_limit=6.4e7,
                              sigma_clip=True,
                              sigma_clip_low_thresh=3.0,
                              sigma_clip_high_thresh=3.0,
                              scale=self.mode)

        foo = master_flat[200:-200, 200:-200].data
        w, h = foo.shape
        w = np.random.random_integers(0, w, 20)
        h = np.random.random_integers(0, h, 20)
        foo = foo[w, h].ravel()
        foo = stats.mode(foo)[0]

        master_flat.data = master_flat.data / foo
        master_flat.header = hdr
        master_flat.write('nSFLAT_{:s}.fits'.format(hdr['FILTERS']), clobber=True)

if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(
        description="Combine images into a merged single file."
    )

    parser.add_argument(
        'input_files',
        nargs='+'
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
        type=str, default='o.fits',
        help='Name of the output fits file.'
    )

    args = parser.parse_args()

    flat_combine = FlatCombine(verbose=not args.quiet, debug=args.debug)
    flat_combine.run(args.input_files, output_file=args.output)
