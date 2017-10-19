#!/usr/bin/env python 
# -*- coding: utf8 -*-
"""
    2D Map Extractor

    This script is used to calculate the main 2D maps from a data-cube. All
    the maps are saved inside a single FITS file. Each maps is saved in a
    different extension.

    [0] Main extension - Contains the main header
"""
from __future__ import division, print_function

import datetime
import itertools
import logging
import os
import sys
from multiprocessing import Pool, Process

import astropy.io.fits as pyfits
import numpy as np
from astropy.modeling import models, fitting
from scipy import ndimage, signal, stats


def signal_handler(s, frame):
    sys.exit()

def perform_2dmap_extraction(_input_filename, log, n=4, algorithm='direct'):
    """
    Perform the 2D-Map extraction using `multiprocessing` and
    `astropy.modeling`.

    Parameters
    ----------
        _input_filename : str
            Input filename containing the data-cube.
        log : logging.Logger
            A logger instance
        n : int
            The number of simultaneous processes that will be executed.
        gaussian : bool
            Perform Gaussian fit instead of Lorentzian fit?
    Returns
    -------
        results : numpy.ndarray
            A (X x Y x 3) array containining:
             - m0: the Lorentzian amplitude,
             - m1: the Lorentzian center.
             - m2: the Lorentzian width.
            or
            A (X x Y x 3) array containining:
             - m0: the Gaussian amplitude,
             - m1: the Gaussian center.
             - m2: the Gaussian width.
    """

    if not isinstance(_input_filename, str):
        raise TypeError, ('_input_filename expected to be string. '
                          '{}s found.'.format(_input_filename.__class__))

    if not isinstance(log, logging.Logger):
        raise TypeError, ('`log` expected to be a logging.Logger instance. '
                          '{}s found.'.format(log.__class__))

    if not isinstance(n, int):
        raise TypeError, ('`n` expected to be a `int` instance. '
                          '{}s found.'.format(n.__class__))

    if not os.path.exists(_input_filename):
        raise IOError, ('{}s file not could not be open for '
                        'reading.'.format(_input_filename))

    # Load data ---
    log.info(' Loading data from: {0:s}'.format(_input_filename))
    header = pyfits.getheader(_input_filename)
    x = np.arange(header['NAXIS1'], dtype=int)
    y = np.arange(header['NAXIS2'], dtype=int)

    # Using astropy fitter and model ---
    if algorithm in 'direct':
        fitter = DirectMeasure(_input_filename)
    elif algorithm in 'lorentzian':
        fitter = FitLorentzian(_input_filename)
    elif algorithm in 'gaussian':
        fitter = FitGaussian(_input_filename)
    else:
        raise IOError, 'Wrong algorithm input: {:s}'.format(algorithm)

    p = Pool(n)
    results = None

    log.info(' Extracting 2D Maps using: {:s}'.format(algorithm))
    loading = Process(target=stand_by, name="stand_by", args=[log.level])
    loading.start()
    try:
        results = p.map_async(fitter, itertools.product(x, y)).get(99999999)
    except KeyboardInterrupt:
        log.info('\n\nYou pressed Ctrl+C!')
        log.info('Leaving now. Bye!\n')
        pass
    p.close()
    p.join()
    loading.terminate()

    return np.array(results)


def clean_header(header):
    """
    Cleans the input header by removing some useless cards.

    Parameter
    ---------
        header : astropy.io.fits.Header

    Return
    ------
        new_header : astropy.io.fits.Header
    """
    keys = [
        'NEXTEND',
        'PREFLASH',
        'ADC',
        'CRPIX3',
        'CRVAL3',
        'CDELT3',
        'C3_3',
        'CR3_3',
        'CUNITS3'
    ]

    try:
        for key in keys:
            del header[key]
    except KeyError:
        pass

    return header


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
            - pool_size (int)
            - quiet (bool)
            - output (str|None)
    """
    from argparse import ArgumentParser

    parser = ArgumentParser(
        description="This script is used to calculate the main 2D maps from a "
                    "data-cube. All the maps are saved inside a single FITS "
                    "file. Each maps is saved in a different extension."
    )
    parser.add_argument(
        '-a', '--algorithm', type=str, default='direct', nargs='?',
        const='direct', help="Use [lorentzian|gaussian|direct] to find" +
                             "the maps. 'direct' is the default"
    )
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help="Enable debug mode."
    )
    parser.add_argument(
        'filename', type=str, help="Input data-cube name."
    )
    parser.add_argument(
        '-o', '--output', default=None, type=str,
        help='Number of the output file. Each map is saved inside a different '
             'extention. If not given, a new file is created for each 2d-map.'
    )
    parser.add_argument(
        '-p', '--pool_size', default=4, type=int,
        help='Number of parallel processes (Default: 4)'
    )
    parser.add_argument(
        '-q', '--quiet', action='store_true',
        help="Run program quietly. true/[FALSE]"
    )
    parser.add_argument(
        '-w', '--wavelength', type=float, default=None,
        help="The rest wavelength if you want to get your maps in km/s instead."
    )
    args = parser.parse_args()

    return args


def stand_by(level=logging.NOTSET):
    """
    A silly method that keeps the terminal alive so the user knows that
    this programs is still running. :-)
    """
    from time import sleep

    output = ['/', '-', '\\', '|']
    i = 0

    if level in [logging.NOTSET, logging.WARN, logging.ERROR]:
        return

    while True:
        sys.stdout.write("\r [{:s}]".format(output[i]))
        sys.stdout.flush()
        sleep(0.5)
        i += 1
        i %= 4

    return


def write_results(_results, _input_file, _output_file, algorithm='direct',
                  wavelength=None):

    """
    Write the results to one or more FITS file.

    _results : numpy.ndarray
        A (X x Y x 3) numpy.ndarray that contains the results of the
        Gaussian fitting process performed in every pixel.
    _input_file : str
        The orginal input filename.
    _output_file : None or str
        If _output_file is a string, then all the results are stored inside a
        single FITS file with the name stored in it. Each result will be saved
        in a different extention.

        If _output_file is None, then the original name is appended with '.m*'
        and a single file is used to store each results. '.m0' contains the
        Gaussian peak value, '.m1' contains the Gaussian center and '.m2'
        contains the Gaussian stddev.
    Gaussian : bool
        Use Gaussian instead of Lorentzian
    wavelength : float / None
        If the wavelength is given, this method automatically convert the maps
        from Angstrom to km/s.
    """
    from astropy import constants

    header = pyfits.getheader(_input_file)
    header = clean_header(header)
    x = int(header['NAXIS1'])
    y = int(header['NAXIS2'])

    m0 = _results[:, 0]  # Amplitude
    m1 = _results[:, 1]  # Mean
    m2 = _results[:, 2]  # STDDEV
    m3 = _results[:, 3]  # CONT

    m0 = m0.reshape((x, y)).T
    m1 = m1.reshape((x, y)).T
    m2 = m2.reshape((x, y)).T
    m3 = m3.reshape((x, y)).T

    m0 = np.array(m0, dtype=np.float32)
    m1 = np.array(m1, dtype=np.float32)
    m2 = np.array(m2, dtype=np.float32)
    m3 = np.array(m3, dtype=np.float32)

    h1 = header
    h2 = header

    h1.append("M1_MEAN", np.mean(m1))
    h1.append("M1_STDEV", np.std(m1))

    h2.append("M2_MEAN", np.mean(m2))
    h2.append("M2_STDEV", np.std(m2))

    # Using astropy fitter and model ---
    if algorithm in 'direct':
        i = 'D'
    elif algorithm in 'lorentzian':
        i = 'L'
    elif algorithm in 'gaussian':
        i = 'G'
    else:
        raise (IOError, 'Wrong algorithm input: {:s}'.format(algorithm))

    if wavelength is not None:

        m1 = (m1 - wavelength) / wavelength * constants.c.to('km/s').value
        m2 = m2 / wavelength * constants.c.to('km/s').value

        h1.set('UNITS', 'km/s')
        h2.set('UNITS', 'km/s')

    else:

        h1.set('UNITS', 'Angstrom')
        h2.set('UNITS', 'Angstrom')

    if _output_file is None:

        pyfits.writeto(
            _input_file.replace('.fits', '.{:s}m0.fits'.format(i)), data=m0,
            header=header, clobber=True
        )
        pyfits.writeto(
            _input_file.replace('.fits', '.{:s}m1.fits'.format(i)), data=m1,
            header=h1, clobber=True
        )
        pyfits.writeto(
            _input_file.replace('.fits', '.{:s}m2.fits'.format(i)), data=m2,
            header=h2, clobber=True
        )
        pyfits.writeto(
            _input_file.replace('.fits', '.{:s}m3.fits'.format(i)), data=m3,
            header=header, clobber=True
        )

    else:
        if algorithm in 'direct':
            HDUl = pyfits.HDUList()
            HDUl.append(pyfits.PrimaryHDU(header))
            HDUl.append(pyfits.ImageHDU(data=m0, name='Direct_Peak'))
            HDUl.append(pyfits.ImageHDU(data=m1, name='Center',
                                        header=h1))
            HDUl.append(pyfits.ImageHDU(data=m2, name='STDDEV',
                                        header=h2))
            HDUl.append(pyfits.ImageHDU(data=m3, name='CONT',
                                        header=header))
            HDUl.writeto(_output_file, clobber=True)

        elif algorithm in 'lorentzian':
            HDUl = pyfits.HDUList()
            HDUl.append(pyfits.PrimaryHDU(header))
            HDUl.append(pyfits.ImageHDU(data=m0, name='Lorentzian_Peak'))
            HDUl.append(pyfits.ImageHDU(data=m1, name='Lorentzian_Center',
                                        header=h1))
            HDUl.append(pyfits.ImageHDU(data=m2, name='Lorentzian_STDDEV',
                                        header=h2))
            HDUl.append(pyfits.ImageHDU(data=m3, name='Lorentzian_CONT',
                                        header=header))
            HDUl.writeto(_output_file, clobber=True)

        elif algorithm in 'gaussian':
            HDUl = pyfits.HDUList()
            HDUl.append(pyfits.PrimaryHDU(header))
            HDUl.append(pyfits.ImageHDU(data=m0, name='Gaussian_Peak'))
            HDUl.append(pyfits.ImageHDU(data=m1, name='Gaussian_Center',
                                        header=h1))
            HDUl.append(pyfits.ImageHDU(data=m2, name='Gaussian_STDDEV',
                                        header=h2))
            HDUl.append(pyfits.ImageHDU(data=m3, name='Gaussian_CONT',
                                        header=header))
            HDUl.writeto(_output_file, clobber=True)


class MyFitter:

    def __init__(self, filename):
        """
        Parameter
        ---------
            filename : str
                Relative or absolute path to the file that contains a data-cube
                from where the 2D maps will be extracted through gaussian
                fitting.
        """
        self._filename = filename

        # Load the data and do some pre-processing ---
        data = pyfits.getdata(self._filename, memmap=True)
        s = data.mean(axis=2).mean(axis=1)

        # Delete the data that will not be used anymore ---
        del data

        # Find the local maxima ---
        s = ndimage.gaussian_filter1d(s, 3)
        max_args = signal.argrelmax(s, order=3)[0]

        # Get the top of the top ---
        max_s = s[max_args]
        max_arg = np.argmax(max_s)
        self._argmax = max_arg
        self._left = 0
        self._right = s.size - 1

        # Find the safe window ---
        if len(max_args) > 1:

            max_differences = max_arg - max_args
            print(max_differences)

            max_left = max_differences[max_differences < 0]


class FitGaussian(MyFitter):

    def __call__(self, indexes):
        """
        Parameter
        ---------
            indexes : tuple
                Contains two integers that correspond to the X and Y indexes
                that will be used to extract the spectrum from the data-cube and
                fits a gaussian to this extracted spectrum.
        Returns
        -------
            results : list
                A list containing the numerical values of the three gaussian
                parameters met in the fitting processes `peak`, `mean` and
                `stddev`.
        """
        i, j = indexes
        data = pyfits.getdata(self._filename, memmap=True)
        s = data[self._left:self._right, j, i]

        h = pyfits.getheader(self._filename)
        self._z = \
            (np.arange(s.size) - h['CRPIX3'] - 1) * h['CDELT3'] + h['CRVAL3']

        del data
        del h

        # Calculate the continuun --
        cont = stats.mode(s)[0]

        arg_max = self._argmax
        amp = s[arg_max]
        avg = self._z[arg_max]

        fitter = fitting.LevMarLSQFitter()
        g = models.Gaussian1D(amplitude=amp, mean=avg, stddev=2.0) + \
            models.Const1D(amplitude=cont)

        g = fitter(g, self._z, s)

        if  fitter.fit_info['ierr'] not in [1, 2, 3, 4]:
            return [np.nan, np.nan, np.nan, np.nan]

        return [g.amplitude_0.value, g.mean_0.value, g.stddev_0.value,
                g.amplitude_1.value]


class FitLorentzian(MyFitter):

    def __call__(self, indexes):
        """
        Parameter
        ---------
            indexes : tuple
                Contains two integers that correspond to the X and Y indexes
                that will be used to extract the spectrum from the data-cube and
                fits a gaussian to this extracted spectrum.
        Returns
        -------
            results : list
                A list containing the numerical values of the three gaussian
                parameters met in the fitting processes `peak`, `mean` and
                `stddev`.
        """
        i, j = indexes
        data = pyfits.getdata(self._filename, memmap=True)
        s = data[self._left:self._right, j, i]

        h = pyfits.getheader(self._filename)
        self._z = \
            (np.arange(s.size) - h['CRPIX3'] - 1) * h['CDELT3'] + h['CRVAL3']

        del data
        del h

        # Calculate the continuun --
        cont = stats.mode(s)[0]

        # Get the first guess parameters --
        arg_max = self._argmax
        amplitude = s[arg_max]
        x_0 = self._z[arg_max]

        fitter = fitting.LevMarLSQFitter()
        my_model = models.Lorentz1D(amplitude=amplitude, x_0=x_0, fwhm=5.0) + \
                    models.Const1D(amplitude=cont)

        fitted = fitter(my_model, self._z, s)

        if  fitter.fit_info['ierr'] not in [1, 2, 3, 4]:
            return [np.nan, np.nan, np.nan, np.nan]

        return [fitted.amplitude_0.value, fitted.x_0_0.value,
                fitted.fwhm_0.value, fitted.amplitude_1.value]


class DirectMeasure(MyFitter):

    def __call__(self, indexes):
        """
        Parameter
        ---------
            indexes : tuple
                Contains two integers that correspond to the X and Y indexes
                that will be used to extract the spectrum from the data-cube and
                fits a gaussian to this extracted spectrum.
        Returns
        -------
            results : list
                A list containing the numerical values of the three gaussian
                parameters met in the fitting processes `peak`, `mean` and
                `stddev`.
        """
        i, j = indexes
        data = pyfits.getdata(self._filename, memmap=True)
        s = data[self._left:self._right, j, i]

        h = pyfits.getheader(self._filename)
        self._z = \
            (np.arange(s.size) - h['CRPIX3'] - 1) * h['CDELT3'] + h['CRVAL3']

        del data
        del h

        # Calculate center using barycenter ---
        p = s / s.sum()
        x_0 = np.sum(self._z * p)

        # Calculate dispersion ---

        p_min = np.abs(p.min())
        p += p_min
        stddev = np.sqrt(np.sum((self._z - x_0) ** 2 * p))

        # Calculate the amplitude ---
        p -= p_min
        cond = np.where(np.abs(self._z - x_0) <= stddev, True, False)
        flux = np.sum(s[cond])

        # Calculate the continuun --
        cont = stats.mode(s)[0]

        return [flux, x_0, stddev, cont]


if __name__ == '__main__':
    main()
