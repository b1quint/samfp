#!/usr/bin/env python 
# -*- coding: utf8 -*-
from __future__ import division, print_function

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

    def run(self, csv_table, bias_file=None):

        import pandas as pd
        import numpy as np

        from astropy.io import fits as pyfits
        from astropy import units as u
        from ccdproc import CCDData
        from ccdproc import combine
        from samfp import xjoin
        from scipy import stats

        dataframe = pd.read_csv(csv_table)
        dataframe = dataframe[dataframe['OBSTYPE'] == 'SFLAT']
        dataframe = dataframe[dataframe['NEXTEND'] == 4]

        xj = xjoin.SAMI_XJoin(
            clean=True, cosmic_rays=True, verbose=True, bias_file=bias_file
        )
        flats = dataframe['FILTERS'].unique()

        for f in flats:
            self.info('Processing filter {:s}'.format(f))

            flat_list = []
            list_of_files = dataframe[dataframe['FILTERS'] == f]
            list_of_files = list_of_files['FILENAME']
            list_of_files = list_of_files.tolist()

            master_header = pyfits.getheader(list_of_files[0])
            master_header.add_blank()

            for i in range(len(list_of_files)):

                self.debug(list_of_files[i])

                hdr = pyfits.getheader(list_of_files[i])
                data = xj.get_joined_data(list_of_files[i])

                data, hdr, prefix = xj.join_and_process(data, hdr)
                data = CCDData(data, unit=u.adu)

                flat_list.append(data)

            master_flat = combine(flat_list, method='median',
                                  mem_limit=6.4e7,
                                  sigma_clip=True,
                                  sigma_clip_low_thresh=3.0,
                                  sigma_clip_high_thresh=3.0,
                                  scale="mode",
                                  statssec="[200:800,200:800]")

            foo = master_flat[100:-100, 100:-100].data
            w, h = foo.shape
            w = np.random.random_integers(0, w, 20)
            h = np.random.random_integers(0, h, 20)
            foo = foo[w, h].ravel()
            foo = stats.mode(foo)[0]

            master_flat.data = master_flat.data / foo
            master_flat.header = master_header
            master_flat.write('nSFLAT_{:s}.fits'.format(f), clobber=True)

if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(
        description="Combine bias images into a merged single file."
    )

    parser.add_argument(
        '-b', '--bias',
        default=None,
        help="Name of the bias file that will be subtracted from the others."
    )

    parser.add_argument(
        'input_database',
        type=str,
        help="A CSV file containing the information about all the files, "
             "specially the zero files."
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

    args = parser.parse_args()

    zero_combine = FlatCombine(verbose=not args.quiet, debug=args.debug)
    zero_combine.run(args.input_database, bias_file=args.bias)
