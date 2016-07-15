#!/usr/bin/env python2
# -*- coding: utf8 -*-
"""
    SAMI XJoin

    This script simply joins the four existing extensions inside a FITS file
    created during observations with SAMI (SAM Imager). During the process,
    it also fits a 2nd degree polynomium to the OVERSCAN region that is
    subtracted from the corresponding image.

    The user also may want to add flags in order to process the images
    according to the following options (in order):

    - BIAS subtraction;
    - DARK subtraction;
    - Remove hot pixels and cosmic rays;
    - Remove overglow using a long exposure DARK image;
    - Divide by the FLAT;
    - Divide by the exposure time;

    The documentation for each process is shown in the corresponding function.

    Bruno Quint (bquint at ctio.noao.edu)
    May 2016

    Thanks to Andrei Tokovinin and Claudia M. de Oliveira for the ideas that
    were implemented here.
"""

from __future__ import division, print_function

import astropy.io.fits as pyfits
import argparse
import logging as log
import numpy as np
import os

from ccdproc import cosmicray_lacosmic

try:
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    xrange
except NameError:
    # noinspection PyShadowingBuiltins
    xrange = range

# Piece of code from cosmics.py
# We define the laplacian kernel to be used
laplkernel = np.array([[0.0, -1.0, 0.0], [-1.0, 4.0, -1.0], [0.0, -1.0, 0.0]])

# Other kernels :
growkernel = np.ones((3, 3))

# dilation structure for some morphological operations
dilstruct = np.ones((5, 5))
dilstruct[0, 0] = 0
dilstruct[0, 4] = 0
dilstruct[4, 0] = 0
dilstruct[4, 4] = 0


# noinspection PyPep8Naming
class SAMI_XJoin:
    """
    SAMI_XJoin

    This class holds all the methods used to join the extensions within a
    FITS file obtained with SAMI.

    Parameters
    ----------
        list_of_files : list
            A list of input files

        bias_file : str
            The filename of the master bias that will be used in subtraction.

        clean : bool
            Clean bad collumns by taking the median value of the pixels around
            them.

        cosmic_rays : bool
            Clean cosmic rays using LACosmic package. See noted bellow for
            reference.

        dark_file : str
            Master Dark's filename to be used for dark subtraction.

        debug : bool
            Turn on debug mode with lots of printing.

        flat_file : str
            Master Flat filename to be used for normalization.

        glow_file : str
            Master file that contains the lateral glowings sometimes present in
            SAMI's data.

        time : bool
            Divide each pixel's values by the exposure time and update header.

        verbose : bool
            Turn on verbose mode (not so talktive as debug mode).

    See also
    --------
        LACosmic - http://www.astro.yale.edu/dokkum/lacosmic/
    """
    def __init__(self, list_of_files, bias_file=None, clean=False,
                 cosmic_rays=False, dark_file=None, debug=False,
                 flat_file=None, glow_file=None, time=False, verbose=False):
        self.set_verbose(verbose)
        self.set_debug(debug)
        self.main(list_of_files, bias_file=bias_file, clean=clean,
                  cosmic_rays=cosmic_rays, dark_file=dark_file,
                  flat_file=flat_file, glow_file=glow_file, time=time)

        return

    @staticmethod
    def bias_subtraction(data, header, prefix, bias_file):
        """
        Subtract bias from data.

            Parameters
            ----------
                data : numpy.ndarray
                    A 2D numpy array that contains the data.

                header : astropy.io.fits.Header
                    A header that will be updated.

                prefix : str
                    File prefix that is added after each process.

                bias_file: str | None
                    Master Bias filename. If None is given, nothing is done.
        """
        if bias_file is not None:
            bias = pyfits.getdata(os.path.abspath(bias_file))
            data -= bias
            header['BIASFILE'] = bias_file
            header.add_history('Bias subtracted')
            prefix = 'b' + prefix

        return data, header, prefix

    @staticmethod
    def clean_column(_data, x0, y0, yf, n=5):
        """
        Substitutes a single column by the median of the neighbours columns.

        Parameters
        ----------
            _data : numpy.ndarray
                A 2D numpy array that contains the data.

            x0 : int
                X position of the pixel to be cleaned.

            y0 : int
                Start position of the column.

            yf : int
                Final position of the column.

            n : int
                Number of neighbour columns. (Default=5)

        See also
        --------
            SAMI_XJoin.clean_columns
            SAMI_XJoin.clean_line
            SAMI_XJoin.clean_lines
        """
        if not isinstance(_data, np.ndarray):
            raise (TypeError, 'Please, use a np.array as input')

        if _data.ndim is not 2:
            raise (TypeError, 'Data contains %d dimensions while it was '
                              'expected 2 dimensions.')

        t1 = _data[y0:yf, x0 - n:x0]
        t2 = _data[y0:yf, x0 + 1:x0 + n]
        t = np.hstack((t1, t2))
        _data[y0:yf, x0] = np.median(t, axis=1)

        return _data

    def clean_columns(self, _data):
        """
        Clean the known bad columns that exists in most of SAMI's data.

        Parameters
        ----------
            _data : numpy.ndarray
                A 2D numpy array that contains the data.

        See also
        --------
            SAMI_XJoin.clean_column
            SAMI_XJoin.clean_line
            SAMI_XJoin.clean_lines
        """
        if not isinstance(_data, np.ndarray):
            raise (TypeError, 'Please, use a np.array as input')
        if _data.ndim is not 2:
            raise (TypeError, 'Data contains %d dimensions while it was '
                              'expected 2 dimensions.')

        bad_columns = [
            [167, 0, 513],
            [476, 0, 513],
            [602, 0, 513],
            [671, 0, 513],
            [673, 475, 513],
            [810, 0, 513],
            [213, 513, 1024]
        ]

        for column in bad_columns:
            x0 = column[0]
            y0 = column[1]
            yf = column[2]
            _data = self.clean_column(_data, x0, y0, yf)
        return _data

    @staticmethod
    def clean_line(_data, x0, xf, y, n=5):
        """
            Substitutes a single column by the median of the neighbours columns.

            Parameters
            ----------
                _data : numpy.ndarray
                    A 2D numpy array that contains the data.

                x0 : int
                    Start position of the line.

                xf : int
                    Final position of the line.

                y : int
                    Y position of the pixel to be cleaned.

                n : int
                    Number of neighbour columns. (Default=5)

            See also
            --------
                SAMI_XJoin.clean_column
                SAMI_XJoin.clean_columns
                SAMI_XJoin.clean_lines
        """
        if not isinstance(_data, np.ndarray):
            raise (TypeError, 'Please, use a np.array as input')
        if _data.ndim is not 2:
            raise (TypeError, 'Data contains %d dimensions while it was '
                              'expected 2 dimensions.')

        t1 = _data[y - n:y, x0:xf]
        t2 = _data[y + 1:y + n, x0:xf]
        t = np.vstack((t1, t2))
        _data[y, x0:xf] = np.median(t, axis=0)
        return _data

    def clean_lines(self, _data):
        """
        Clean the known bad lines that exists in most of SAMI's data.

        Parameters
        ----------
            _data : numpy.ndarray
                A 2D numpy array that contains the data.

        See also
        --------
            SAMI_XJoin.clean_column
            SAMI_XJoin.clean_columns
            SAMI_XJoin.clean_line
        """
        if not isinstance(_data, np.ndarray):
            raise (TypeError, 'Please, use a np.array as input')
        if _data.ndim is not 2:
            raise (TypeError, 'Data contains %d dimensions while it was '
                              'expected 2 dimensions.')

        bad_lines = [
            [214, 239, 688],
            [477, 516, 490],
            [387, 429, 455],
            [574, 603, 494],
            [574, 603, 493],
            [640, 672, 388],
            [604, 671, 388]
        ]

        for line in bad_lines:
            x0 = line[0]
            xf = line[1]
            y = line[2]
            _data = self.clean_line(_data, x0, xf, y)
        return _data

    def clean_hot_columns_and_lines(self, data, header, prefix, clean):
        """
            Clean known hot columns and lines from SAMI's images.

            Parameters
            ----------
                data : numpy.ndarray
                    A 2D numpy array that contains the data.

                header : astropy.io.fits.Header
                    A header that will be updated.

                prefix : str
                    File prefix that is added after each process.

                clean : bool
                    Should I perform the clean?

            See also
            --------
                SAMI_XJoin.clean_column
                SAMI_XJoin.clean_columns
                SAMI_XJoin.clean_line
                SAMI_XJoin.clean_lines
        """
        if not isinstance(data, np.ndarray):
            raise (TypeError, 'Please, use a np.array as input')

        if data.ndim is not 2:
            raise (TypeError, 'Data contains %d dimensions while it was '
                              'expected 2 dimensions.')

        if not isinstance(header, pyfits.Header):
            raise (TypeError, 'Expected header has invalid type.')

        if not isinstance(prefix, str):
            raise (TypeError, 'Expected string but found %s instead.' %
                   prefix.__class__)

        if not isinstance(clean, bool):
            raise (TypeError, 'Expected boolean but found %s instead.' %
                   clean.__class__)

        if clean is True:
            data = self.clean_columns(data)
            data = self.clean_lines(data)
            header.add_history('Cleaned bad columns and lines.')
            prefix = 'c' + prefix

        return data, header, prefix

    @staticmethod
    def dark_subtraction(data, header, prefix, dark_file=None):
        """
            Subtract the dark file from data and add HISTORY to header.

            Parameters
            ----------
                data : numpy.ndarray
                    A 2D numpy array that contains the data.

                header : astropy.io.fits.Header
                    A header that will be updated.

                prefix : str
                    File prefix that is added after each process.

                dark_file: str | None
                    Master Dark filename. If None is given, nothing is done.
        """
        if not isinstance(data, np.ndarray):
            raise (TypeError, 'Please, use a np.array as input')

        if data.ndim is not 2:
            raise (TypeError, 'Data contains %d dimensions while it was '
                              'expected 2 dimensions.')

        if not isinstance(header, pyfits.Header):
            raise (TypeError, 'Expected header has invalid type.')

        if not isinstance(prefix, str):
            raise (TypeError, 'Expected string but found %s instead.' %
                   prefix.__class__)

        if dark_file is not None:
            dark = pyfits.getdata(dark_file)
            data -= dark
            header['DARKFILE'] = dark_file
            prefix = 'd' + prefix
            header.add_history('Dark subtracted')

        return data, header, prefix

    @staticmethod
    def divide_by_flat(data, header, prefix, flat_file):
        """
            Divide the image by the master flat file and add HISTORY to header.

            Parameters
            ----------
                data : numpy.ndarray
                    A 2D numpy array that contains the data.

                header : astropy.io.fits.Header
                    A header that will be updated.

                prefix : str
                    File prefix that is added after each process.

                flat_file: str | None
                    Master flat filename. If None is given, nothing is done.
        """
        if not isinstance(data, np.ndarray):
            raise (TypeError, 'Please, use a np.array as input')

        if data.ndim is not 2:
            raise (TypeError, 'Data contains %d dimensions while it was '
                              'expected 2 dimensions.')

        if not isinstance(header, pyfits.Header):
            raise (TypeError, 'Expected header has invalid type.')

        if not isinstance(prefix, str):
            raise (TypeError, 'Expected string but found %s instead.' %
                   prefix.__class__)

        if flat_file is not None:
            flat = pyfits.getdata(flat_file)
            data /= flat
            header['FLATFILE'] = flat_file
            header.add_history('Flat normalized')
            prefix = 'f' + prefix

        return data, header, prefix

    @staticmethod
    def divide_by_exposuretime(data, header, prefix, time):
        """
            Divide the image by the exposure time and add HISTORY to header.

            Parameters
            ----------
                data : numpy.ndarray
                    A 2D numpy array that contains the data.

                header : astropy.io.fits.Header
                    A header that will be updated.

                prefix : str
                    File prefix that is added after each process.

                time: bool
                    Divide image by exposure time?
        """
        if time is True:
            try:
                exptime = float(header['EXPTIME'])
                data /= exptime
                header['UNITS'] = 'COUNTS/s'
                header.add_history('Divided by exposure time.')
                prefix = 't' + prefix
            except KeyError:
                pass

        return data, header, prefix

    @staticmethod
    def get_header(filename):
        """
        Return the header of the primary HDU extension of a FITS file.

        Parameters
        ----------
            filename : str
                Path to the file.
        """
        if not isinstance(filename, str):
            raise (TypeError, 'Expected string. Found %s' % filename.__class__)

        if not os.path.exists(filename):
            raise (IOError, '%s file not found.' % filename)

        fits_file = pyfits.open(filename)
        h0 = fits_file[0].header
        h0.append('UNITS')
        h0.set('UNITS', value='COUNTS', comment='Pixel intensity units.')

        return h0

    @staticmethod
    def get_joined_data(filename):
        """
        Open a FITS image and try to join its extensions in a single array.

        Parameters
        ----------
            filename : str
                Path to the file.
        """
        if not isinstance(filename, str):
            raise (TypeError, 'Expected string. Found %s' % filename.__class__)

        if not os.path.exists(filename):
            raise (IOError, '%s file not found.' % filename)

        fits_file = pyfits.open(filename)
        w, h = str2pixels(fits_file[1].header['DETSIZE'])

        if len(fits_file) is 1:
            log.warning('%s file contains a single extension. ' % fits_file +
                        'Not doing anything')
            return fits_file[0].data

        log.info(' > %s' % filename)

        # Correct for binning
        bin_size = np.array(fits_file[1].header['CCDSUM'].split(' '),
                            dtype=int)
        bw, bh = w[1] // bin_size[0], h[1] // bin_size[1]

        # Create empty full frame
        new_data = np.empty((bh, bw), dtype=float)

        # Process each extension
        for i in range(1, 5):
            tx, ty = str2pixels(fits_file[i].header['TRIMSEC'])
            bx, by = str2pixels(fits_file[i].header['BIASSEC'])

            data = fits_file[i].data
            trim = data[ty[0] - 1:ty[1], tx[0] - 1:tx[1]]
            bias = data[by[0] - 1:by[1], bx[0] - 1:bx[1]]

            # Collapse the bias columns to a single column.
            bias = np.median(bias, axis=1)

            # Fit and remove OVERSCAN
            x = np.arange(bias.size) + 1
            bias_fit_pars = np.polyfit(x, bias, 2)  # Last par = inf
            bias_fit = np.polyval(bias_fit_pars, x)
            bias_fit = bias_fit.reshape((bias_fit.size, 1))
            bias_fit = np.repeat(bias_fit, trim.shape[1], axis=1)

            trim = trim - bias_fit
            dx, dy = str2pixels(fits_file[i].header['DETSEC'])
            dx, dy = dx // bin_size[0], dy // bin_size[1]
            new_data[dy[0]:dy[1], dx[0]:dx[1]] = trim

        return new_data

    def main(self, list_of_files, bias_file=None, clean=False,
             cosmic_rays=False, dark_file=None, flat_file=None,
             glow_file=None, time=False):
        """
        Main method used to:
            1. Join data
            2. Read header
            3. Remove central bad columns and lines
            4. Subtract BIAS
            5. Subtract DARK
            6. Remove cosmic rays and hot pixels
            7. Remove lateral glows
            8. Divide by FLAT
            9. Divide by exposure time
            10. Clean hot columns and lines

        Parameters
        ----------
            list_of_files : list
                A list of input files

            bias_file : str
                The filename of the master bias that will be used in
                subtraction.

            clean : bool
                Clean bad collumns by taking the median value of the pixels
                around them.

            cosmic_rays : bool
                Clean cosmic rays using LACosmic package. See noted bellow for
                reference.

            dark_file : str
                Master Dark's filename to be used for dark subtraction.

            flat_file : str
                Master Flat filename to be used for normalization.

            glow_file : str
                Master file that contains the lateral glowings sometimes present
                 in SAMI's data.

            time : bool
                Divide each pixel's values by the exposure time and update
                header.
        """

        self.print_header()
        log.info(' Processing data')
        list_of_files = sorted(list_of_files)

        for filename in list_of_files:
            prefix = "xj"

            # Get joined data
            try:
                data = self.get_joined_data(filename)
            except IOError:
                log.warning('%s file does not exists' % filename)
                continue

            # Build header
            header = self.get_header(filename)

            # Removing bad column and line
            data = self.remove_central_bad_columns(data)

            # BIAS subtraction
            data, header, prefix = self.bias_subtraction(
                data, header, prefix, bias_file
            )

            # DARK subtraction
            data, header, prefix = self.dark_subtraction(
                data, header, prefix, dark_file
            )

            # Remove cosmic rays and hot pixels
            data, header, prefix = self.remove_cosmic_rays(
                data, header, prefix, cosmic_rays
            )

            # Remove lateral glows
            data, header, prefix = self.remove_glows(
                data, header, prefix, glow_file
            )

            # FLAT division
            data, header, prefix = self.divide_by_flat(
                data, header, prefix, flat_file
            )

            # Normalize by the EXPOSURE TIME
            data, header, prefix = self.divide_by_exposuretime(
                data, header, prefix, time
            )

            # Clean known bad columns and lines
            data, header, prefix = self.clean_hot_columns_and_lines(
                data, header, prefix, clean
            )

            # Writing file
            header.add_history('Extensions joined using "sami_xjoin"')
            path, filename = os.path.split(filename)
            pyfits.writeto(os.path.join(path, prefix + filename), data,
                           header, clobber=True)

        log.info("\n All done!")

    @staticmethod
    def print_header():
        """
        Simply prints a message at the beginning.
        """
        msg = (
            "\n SAMI - Join Extensions"
            " by Bruno Quint (bquint@astro.iag.usp.br)"
            " Mar 2015 - Version 0.4"
            "\n Starting program.")
        log.info(msg)

    @staticmethod
    def remove_cosmic_rays(data, header, prefix, cosmic_rays):
        """
        Use LACosmic to remove cosmic rays.

        Parameters
        ----------
            data : numpy.ndarray
                2D Array containing the data

            header : astropy.io.fits.Header
                FITS Header to store HISTORY

            prefix : str
                Filename prefix to flag images that were clean.

            cosmic_rays : bool
                Flag to indicate if cosmic rays removal should be performed.
        """
        if cosmic_rays:
            data, _ = cosmicray_lacosmic(data, gain=2.6, readnoise=10.0,
                                         sigclip=2.5, sigfrac=0.3, objlim=5.0)
            data /= 2.6

            header.set('UNITS', 'adu')
            header.set('BUNIT', 'adu')
            header.add_history(
                'Cosmic rays and hot pixels removed using LACosmic')
            prefix = 'r' + prefix

        return data, header, prefix

    def remove_glows(self, data, header, prefix, glow_file):
        """
        Remove lateral glows by scaling the glows in the `glow_file` based
         on `data` and subtracting it.

        Parameters
        ----------
            data : numpy.ndarray
                2D Array containing the data

            header : astropy.io.fits.Header
                FITS Header to store HISTORY

            prefix : str
                Filename prefix to flag images that were clean.

            glow_file : str
                Path to a long dark file that contains the lateral glow.
        """
        if glow_file is not None:
            # Create four different regions.
            regions = [
                [np.median(data[539:589, 6:56]),  # Top Left
                 np.median(data[539:589, 975:1019])],  # Top Right
                [np.median(data[449:506, 6:56]),  # Bottom Left
                 np.median(data[449:506, 975:1019])]  # Bottom Right
            ]
            min_std_region = np.argmin(regions) % 2

            # The upper reg has background lower or equal to the lower reg
            midpt1 = regions[0][min_std_region]
            midpt2 = regions[1][min_std_region]
            diff = midpt2 - midpt1

            dark = pyfits.getdata(glow_file)
            dark = self.clean_columns(dark)
            dark = self.clean_lines(dark)

            dark_regions = [
                [np.median(dark[539:589, 6:56]),  # Top Left
                 np.median(dark[539:589, 975:1019])],  # Top Right
                [np.median(dark[449:506, 6:56]),  # Bottom Left
                 np.median(dark[449:506, 975:1019])]  # Bottom Right
            ]

            dark_midpt1 = dark_regions[0][min_std_region]
            dark_midpt2 = dark_regions[1][min_std_region]

            dark_diff = dark_midpt2 - dark_midpt1
            dark -= dark_midpt1

            k = diff / dark_diff
            temp_dark = dark * k
            data -= midpt1
            data -= temp_dark

            # print(k)

            header.add_history('Lateral glow removed using %s file' % glow_file)
            prefix = 'g' + prefix

        return data, header, prefix

    @staticmethod
    def set_debug(debug):
        """
        Turn on debug mode.

        Parameter
        ---------
            debug : bool
        """
        if debug:
            log.basicConfig(level=log.DEBUG, format='%(message)s')

    @staticmethod
    def set_verbose(verbose):
        """
        Turn on verbose mode.

        Parameter
        ---------
            verbose : bool
        """
        if verbose:
            log.basicConfig(level=log.INFO, format='%(message)s')
        else:
            log.basicConfig(level=log.WARNING, format='%(message)s')

    @staticmethod
    def remove_central_bad_columns(data):
        """
        Remove central bad columns at the interface of the four extensions.

        Parameter
        ---------
            data : numpy.ndarray
                2D Array containing the data.
        """
        n_rows, n_columns = data.shape

        # Copy the central bad columns to a temp array
        temp_column = data[:, n_columns // 2 - 1:n_columns // 2 + 1]

        # Shift the whole image by two columns
        data[:, n_columns // 2 - 1:-2] = data[:, n_columns // 2 + 1:]

        # Copy the bad array in the end (right) of the image).
        data[:, -2:] = temp_column

        return data


def str2pixels(my_string):
    """
    Parse a string containing [XX:XX, YY:YY] to pixels.

    Parameter
    ---------
        my_string : str
    """
    my_string = my_string.replace('[', '')
    my_string = my_string.replace(']', '')
    x, y = my_string.split(',')

    x = x.split(':')
    y = y.split(':')

    # "-1" fix from IDL to Python
    x = np.array(x, dtype=int)
    y = np.array(y, dtype=int)

    return x, y


if __name__ == '__main__':
    # Parsing Arguments ---
    parser = argparse.ArgumentParser(
        description="Join extensions existent in a single FITS file."
    )

    parser.add_argument('-b', '--bias', type=str, default=None,
                        help="Consider BIAS file for subtraction.")
    parser.add_argument('-c', '--clean', action='store_true',
                        help="Clean known bad columns and lines by taking the "
                             "median value of their neighbours.")
    parser.add_argument('-d', '--dark', type=str, default=None,
                        help="Consider DARK file for subtraction.")
    parser.add_argument('-D', '--debug', action='store_true',
                        help="Turn on DEBUG mode (overwrite quiet mode).")
    parser.add_argument('-f', '--flat', type=str, default=None,
                        help="Consider FLAT file for division.")
    parser.add_argument('-g', '--glow', type=str, default=None,
                        help="Consider DARK file to correct lateral glows.")
    parser.add_argument('-q', '--quiet', action='store_true',
                        help="Run quietly.")
    parser.add_argument('-r', '--rays', action='store_true',
                        help='Use LACosmic.py to remove cosmic rays and hot '
                             'pixels.')
    parser.add_argument('-t', '--exptime', action='store_true',
                        help="Divide by exposure time.")
    parser.add_argument('files', metavar='files', type=str, nargs='+',
                        help="input filenames.")

    pargs = parser.parse_args()

    SAMI_XJoin(pargs.files, bias_file=pargs.bias, clean=pargs.clean,
               cosmic_rays=pargs.rays, dark_file=pargs.dark, debug=pargs.debug,
               flat_file=pargs.flat, glow_file=pargs.glow, time=pargs.exptime,
               verbose=not pargs.quiet)
