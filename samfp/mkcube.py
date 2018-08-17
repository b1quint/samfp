#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
    SAMI Make Cube

    This file gets several FITS images and put them together inside a single
    FITS file with three dimensions (data-cube).

    Todo
    ----
    - Treat error case multiple extensions.

"""

from __future__ import absolute_import, division, print_function

import astropy.io.fits as pyfits
import argparse
import itertools
import numpy as np
import pandas as pd

from .tools import io, version
from .io.logger import get_logger

logger = get_logger("MakeCube")

__author__ = 'Bruno Quint'


def main():

    # Parsing Arguments -------------------------------------------------------
    parser = argparse.ArgumentParser(
        description="Build a data-cube from image files.")

    parser.add_argument('-a', '--algorithm', metavar='algorithm', type=str,
                        default='average',
                        help="Algorithm used when combining images per "
                             "frame (average | median | sum)")

    parser.add_argument('-b', '--binning', type=int, nargs=2, default=(1, 1),
                        help='New binning to be applied to the data-cube')

    parser.add_argument('-d', '--debug', action='store_true',
                        help="Run debug mode.")

    parser.add_argument('-o', '--output', metavar='output', type=str,
                        default="cube.fits", help="Name of the output cube.")

    parser.add_argument('-q', '--quiet', action='store_true',
                        help="Run quietly.")

    parser.add_argument('files', metavar='files', type=str, nargs='+',
                        help="input filenames.")

    parsed_args = parser.parse_args()

    if parsed_args.quiet:
        logger.setLevel('NOTSET')
    elif parsed_args.debug:
        logger.setLevel('DEBUG')
    else:
        logger.setLevel('INFO')

    logger.info("")
    logger.info("SAM-FP Tools: mkcube")
    logger.info("by Bruno Quint (bquint@ctio.noao.edu)")
    logger.info("version {:s}".format(version.__str__))
    logger.info("Starting program.")
    logger.info("")

    make_cube(parsed_args.files,
              output=parsed_args.output,
              combine_algorithm=parsed_args.algorithm,
              binning=parsed_args.binning)


def make_cube(list_of_files, z_key='FAPEROTZ', combine_algorithm='average',
              output='cube.fits', binning=(1, 1)):
    """
    Stack FITS images within a single FITS data-cube.

    Parameters
    ----------
        list_of_files : list
            A list of strings containing the path to the input fits files.


        z_key : str
            The wildcard name responsible to store the FP gap size in *bcv*
            units.

        combine_algorithm : string
            The algorithm used to combine several images into a single frame
            (average|median|sum)

        output : str
            Name of the output data-cube.

        binning : list or tuple
            Binning to be applied to the data-cube when mounting it.
    """

    assert isinstance(list_of_files, list)
    list_of_files.sort()

    logger.debug('Create table')
    df = pd.DataFrame(columns=['filename', 'nrows', 'ncols', 'z'])

    logger.debug('Filling the table')
    for f in list_of_files:
        logger.debug('Read %s file' % f)
        hdr = pyfits.getheader(f)
        ds = pd.Series({
            'filename': f,
            'nrows': int(hdr['naxis1']),
            'ncols': int(hdr['naxis2']),
            'z': int(hdr[z_key])
        })
        df = df.append(ds, ignore_index=True)

    logger.debug('%d files with different number of rows' % len(
        df['nrows'].unique()))
    logger.debug('%d files with different number of columns' % len(
        df['ncols'].unique()))
    logger.debug('%d files with different Z' % len(df['z'].unique()))

    if len(df['nrows'].unique()) is not 1:
        raise (
            IOError, 'Height mismatch for %d files' % len(df['nrows'].unique()))

    if len(df['ncols'].unique()) is not 1:
        raise (
            IOError, 'Width mismatch for %d files' % len(df['ncols'].unique()))

    nrows = int(df['nrows'].unique() // binning[0])
    ncols = int(df['ncols'].unique() // binning[1])
    nchan = len(df['z'].unique())

    nrows = int(nrows)
    ncols = int(ncols)
    nchan = int(nchan)

    logger.info('Creating data-cube with shape')
    logger.info('[%d, %d, %d]' % (nrows, ncols, nchan))
    cube = np.zeros((nchan, ncols, nrows))

    z_array = df['z'].unique()
    z_array.sort()
    z_array = z_array[::-1]  # Reverse array so lambda increases inside the cube

    combine_algorithm = combine_algorithm.lower()
    if combine_algorithm in ['mean', 'average']:
        combine = np.mean
    elif combine_algorithm in ['median']:
        combine = np.median
    elif combine_algorithm in ['sum']:
        combine = np.sum
    else:
        raise ValueError('"combine_algorith" kwarg must be average/median/sum')

    logger.info('Filling data-cube')
    x, y = range(binning[0]), range(binning[1])

    # Build data-cube
    for i in range(z_array.size):
        logger.debug('Processing channel %03d - z = %.2f' % (i + 1, z_array[i]))
        files = df[df['z'] == z_array[i]]['filename'].tolist()
        temp_cube = np.zeros((len(files), ncols, nrows))

        # Build temporary data-cube for each frame before combine it
        for j in range(len(files)):
            temp_image = pyfits.getdata(files[j])

            # Binning images ---
            for (m, n) in itertools.product(x, y):
                temp_cube[j] += temp_image[n::binning[1], m::binning[0]]

        cube[i] = combine(temp_cube, axis=0)

    logger.info('Find Z solution')
    z = np.arange(z_array.size) + 1
    p = np.polyfit(z, z_array, deg=1)
    delta_z = p[0]
    z_zero = np.polyval(p, 1)

    hdr.set('CRPIX3', 1, 'Reference channel')
    hdr.set('CRVAL3', z_zero, 'Reference channel value')
    hdr.set('CUNIT3', 'bcv', 'Units in Z')
    hdr.set('CDELT3', delta_z, 'Average increment in Z')
    hdr.set('CR3_3', delta_z, 'Average increment in Z')
    hdr.set('C3_3', delta_z, 'Average increment in Z')

    # Saving filenames in the header ---
    hdr.add_history('Cube mounted using `mkcube`')
    for i in range(z_array.size):
        files = df[df['z'] == z_array[i]]['filename'].tolist()
        for j in range(len(files)):
            hdr.append(('CHAN_%03d' % (i + 1), files[j],
                        'z = %+04d' % z_array[i]))
    hdr.add_blank('', after='CHAN_%03d' % (i + 1))
    hdr.add_blank('', before='CHAN_001')
    hdr.add_blank('--- Channels and Files ---', before='CHAN_001')

    filename = output
    output = io.safe_save(output, verbose=True)

    logger.info('Writing file to {:s}'.format(output))
    pyfits.writeto(output, cube, hdr, overwrite=True)

    logger.debug(pd.DataFrame(data={'x': z,
                                 'y': z_array,
                                 'fit_y': np.polyval(p, z),
                                 'round_fit': np.round(np.polyval(p, z))}))
    logger.debug(p)

    return


if __name__ == '__main__':
    main()
