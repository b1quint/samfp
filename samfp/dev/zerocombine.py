#!/usr/bin/env python 
# -*- coding: utf8 -*-
from __future__ import division, print_function

__author__ = 'Bruno Quint'


class ZeroCombine:

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

    def run(self, csv_table, output='o.fits'):

        import pandas as pd
        from astropy.io import fits as pyfits
        from astropy import units as u
        from ccdproc import CCDData, combine
        from samfp import xjoin
        from samfp.globals import csv_columns
        from os.path import exists

        dataframe = pd.read_csv(csv_table)
        dataframe = dataframe.fillna(' ')
        dataframe = dataframe[dataframe['OBJECT'].str.contains('MASTER') == False]
        dataframe = dataframe[dataframe['OBSTYPE'] == 'ZERO']
        dataframe = dataframe[dataframe['NEXTEND'] == 4]
        list_of_files = dataframe['FILENAME'].tolist()

        xj = xjoin.SAMI_XJoin(clean=True, cosmic_rays=True, verbose=True)
        bias_list = []

        master_header = pyfits.getheader(list_of_files[0])
        master_header.set('OBJECT', 'MASTER BIAS')
        master_header.set('NEXTEND', 1)
        master_header.add_blank()
        master_header.set('ZCOMB_A', 'median', 'zerocombine algorithm')
        master_header.set('ZCOMB_SC', True, 'sigma clip?')
        master_header.set('ZCOMB_LT', 3.0, 'sigclip low thresh')
        master_header.set('ZCOMB_HT', 3.0, 'sigclip high thresh')

        self.info('Loading BIAS files to be combined:')
        for i in range(len(list_of_files)):
            f = list_of_files[i]
            if not exists(f):
                self.warn('{:s} file could not be open for reading'.format(f))

            self.info(" {:s}".format(f))

            hdr = pyfits.getheader(f)
            data = xj.get_joined_data(f)

            data, hdr, prefix = xj.join_and_process(data, hdr)
            data = CCDData(data, unit=u.adu)

            bias_list.append(data)
            master_header.set('ZCOMB_{:02}'.format(i), f, '')

        master_bias = combine(bias_list, method='median',
                              mem_limit=6.4e7,
                              sigma_clip=True,
                              sigma_clip_low_thresh=3.0,
                              sigma_clip_high_thresh=3.0)
        master_bias.header = master_header
        master_bias.write(output, clobber=True)

        del dataframe
        del data
        del hdr
        del prefix

        df = pd.read_csv(csv_table)
        df = df[df['OBJECT'].str.contains('MASTER') == False]
        df.append({c: master_header[c] for c in csv_columns}, ignore_index=True)
        df.drop_duplicates()
        df.to_csv(csv_table)

if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(
        description="Combine bias images into a merged single file."
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

    parser.add_argument(
        '-o', '--output',
        type=str, default='master_bias.fits',
        help='Name of the output fits file.'
    )

    args = parser.parse_args()

    zero_combine = ZeroCombine(verbose=not args.quiet, debug=args.debug)
    zero_combine.run(args.input_database, output=args.output)
