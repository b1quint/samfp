#!/usr/bin/python2
# -*- coding: utf8 -*-
"""
    SAMI Make Cube

    This file gets several FITS images and put them together inside a single
    FITS file with three dimensions (data-cube).

    Todo
    ----
    - Treat error case multiple extensions.

"""

from __future__ import division, print_function

import astropy.io.fits as pyfits
import argparse
import itertools
import logging as log
import numpy as np
import pandas as pd

__author__ = 'Bruno Quint'

log.basicConfig(format='%(levelname)s: %(name)s(%(funcName)s): %(message)s',
                level=log.INFO)


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

    log.debug('Create table')
    df = pd.DataFrame(columns=['filename', 'nrows', 'ncols', 'z'])

    log.debug('Filling the table')
    for f in list_of_files:
        log.debug('Read %s file' % f)
        hdr = pyfits.getheader(f)
        ds = pd.Series({
            'filename': f,
            'nrows': int(hdr['naxis1']),
            'ncols': int(hdr['naxis2']),
            'z': int(hdr[z_key])
        })
        df = df.append(ds, ignore_index=True)

    log.debug('%d files with different number of rows' % len(
        df['nrows'].unique()))
    log.debug('%d files with different number of columns' % len(
        df['ncols'].unique()))
    log.debug('%d files with different Z' % len(df['z'].unique()))

    if len(df['nrows'].unique()) is not 1:
        raise (
        IOError, 'Height mismatch for %d files' % len(df['nrows'].unique()))

    if len(df['ncols'].unique()) is not 1:
        raise (
            IOError, 'Width mismatch for %d files' % len(df['ncols'].unique()))

    nrows = df['nrows'].unique() // binning[0]
    ncols = df['ncols'].unique() // binning[1]
    nchan = len(df['z'].unique())

    log.info('Creating data-cube with shape')
    log.info('[%d, %d, %d]' % (nrows, ncols, nchan))
    cube = np.zeros((nchan, ncols, nrows))

    z_array = df['z'].unique()
    z_array.sort()
    z_array = z_array[::-1] # Reverse array so lambda increases inside the cube

    combine_algorithm = combine_algorithm.lower()
    if combine_algorithm in ['mean', 'average']:
        combine = np.mean
    elif combine_algorithm in ['median']:
        combine = np.median
    elif combine_algorithm in ['sum']:
        combine = np.sum
    else:
        raise ValueError('"combine_algorith" kwarg must be average/median/sum')

    log.info('Filling data-cube')
    x, y = range(binning[0]), range(binning[1])

    # Build data-cube
    for i in range(z_array.size):
        log.debug('Processing channel %03d - z = %.2f' % (i + 1, z_array[i]))
        files = df[df['z'] == z_array[i]]['filename'].tolist()
        temp_cube = np.zeros((len(files), ncols, nrows))

        # Build temporary data-cube for each frame before combine it
        for j in range(len(files)):
            temp_image = pyfits.getdata(files[j])

            # Binning images ---
            for (m, n) in itertools.product(x, y):
                temp_cube[j] += temp_image[n::binning[1], m::binning[0]]

        cube[i] = combine(temp_cube, axis=0)

    log.info('Find Z solution')
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

    filename = output
    output = safesave(output, verbose=True)

    log.info('Writing file to %s' % output)
    pyfits.writeto(output, cube, hdr, clobber=True)

    log.debug(pd.DataFrame(data={'x': z,
                             'y': z_array,
                             'fit_y': np.polyval(p, z),
                             'round_fit': np.round(np.polyval(p, z))}))
    log.debug(p)

    return


def safesave(name, overwrite=False, verbose=False):
    """
    This is a generic method used to check if a file called 'name'
    already exists. If so, it starts some interaction with the user.

    Parameters:
        name : str
            The name of the file that will be written in the future.

        overwrite : bool
            If False, this method will interact with the user to ask if 'name'
            file shall be overwritten or if a new name will be given. If True,
            'name' file is automatically overwritten.

        verbose : bool
            force verbose mode on even when overwrite is automatic.
    """
    import os
    import sys

    v = False if (overwrite is True) else True
    if v:
        print("\n Writing to output file %s" % name)

    while os.path.exists(name):

        if overwrite in ['y', 'Y', True]:
            if v or verbose:
                print(" Overwriting %s file." % name)
            os.remove(name)

        elif overwrite in ['', 'n', 'N', False]:
            name = input("   Please, enter a new filename:\n   > ")

        elif overwrite in ['q']:
            if v:
                print(" Exiting program.")
            sys.exit()

        else:
            overwrite = input("   '%s' file exist. Overwrite? (y/[n])"% name)
            if v:
                print(" Writing data-cube to %s" % name)

    return name


if __name__ == '__main__':

    # Parsing Arguments -------------------------------------------------------
    parser = argparse.ArgumentParser(
        description="Build a data-cube from image files.")

    parser.add_argument('-a','--algorithm', metavar='algorithm', type=str,
                        default='average',
                        help="Algorithm used when combining images per "
                             "frame (average | median | sum)")

    parser.add_argument('-b', '--binning', type=int, nargs=2, default=(1, 1),
                        help='New binning to be applied to the data-cube')

    parser.add_argument('-d', '--debug', action='store_true',
                        help="Run debug mode.")

    parser.add_argument('-o','--output', metavar='output', type=str,
                        default="cube.fits", help="Name of the output cube.")

    parser.add_argument('-q','--quiet', action='store_true',
                        help="Run quietly.")

    parser.add_argument('files', metavar='files', type=str, nargs='+',
                        help="input filenames.")

    parsed_args = parser.parse_args()

    if parsed_args.quiet:
        log.basicConfig(level=log.ERROR)

    if parsed_args.debug:
        log.basicConfig(level=log.DEBUG)

    make_cube(parsed_args.files,
              output=parsed_args.output,
              combine_algorithm=parsed_args.algorithm,
              binning=parsed_args.binning)
    
    
