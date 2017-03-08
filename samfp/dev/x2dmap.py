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
from scipy.stats import mode as stats_mode

__author__ = 'Bruno C. Quint'
__date__ = '2016.08.09'
__version__ = '1.0'


# noinspection PyUnusedLocal,PyUnusedLocal
def signal_handler(s, frame):
    sys.exit()


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
    log.info('\n 2D Map Extractor')
    log.info(' by {0}'.format(__author__))
    log.info(' Version {0} - {1}\n'.format(__version__, __date__))

    # Let's start to count the time ---
    tstart = datetime.datetime.now()
    log.debug(' [{0}] Script Start'.format(tstart.strftime('%H:%M:%S')))

    # Perform the 2D-Map Extraction ---
    results = perform_2dmap_extraction(
        args.filename, log, args.pool_size, args.algorithm
    )

    # Write the results to a FITS file ---
    write_results(
        results, args.filename, args.output, args.algorithm,
        wavelength=args.wavelength
    )

    # Now I am good. The script is already done ---
    tend = datetime.datetime.now()
    delta_t = tend - tstart

    log.info('')
    log.debug(' [{0}] Script finished.'.format(tend.strftime('%H:%M:%S')))
    log.debug(' Total time elapsed: {:s}'.format(str(delta_t)))
    log.info('All done.')


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
        raise (TypeError, '_input_filename expected to be string. '
                          '{}s found.'.format(_input_filename.__class__))

    if not isinstance(log, logging.Logger):
        raise (TypeError, '`log` expected to be a logging.Logger instance. '
                          '{}s found.'.format(log.__class__))

    if not isinstance(n, int):
        raise (TypeError, '`n` expected to be a `int` instance. '
                          '{}s found.'.format(n.__class__))

    if not os.path.exists(_input_filename):
        raise (IOError, '{}s file not could not be open for '
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
        raise (IOError, 'Wrong algorithm input: {:s}'.format(algorithm))

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

    m0 = m0.reshape((x, y)).T
    m1 = m1.reshape((x, y)).T
    m2 = m2.reshape((x, y)).T

    m0 = np.array(m0, dtype=np.float32)
    m1 = np.array(m1, dtype=np.float32)
    m2 = np.array(m2, dtype=np.float32)

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

    else:
        if algorithm in 'direct':
            HDUl = pyfits.HDUList()
            HDUl.append(pyfits.PrimaryHDU(header))
            HDUl.append(pyfits.ImageHDU(data=m0, name='Direct_Peak'))
            HDUl.append(pyfits.ImageHDU(data=m1, name='Center',
                                        header=h1))
            HDUl.append(pyfits.ImageHDU(data=m2, name='STDDEV',
                                        header=h2))
            HDUl.writeto(_output_file, clobber=True)

        elif algorithm in 'lorentzian':
            HDUl = pyfits.HDUList()
            HDUl.append(pyfits.PrimaryHDU(header))
            HDUl.append(pyfits.ImageHDU(data=m0, name='Lorentzian_Peak'))
            HDUl.append(pyfits.ImageHDU(data=m1, name='Lorentzian_Center',
                                        header=h1))
            HDUl.append(pyfits.ImageHDU(data=m2, name='Lorentzian_STDDEV',
                                        header=h2))
            HDUl.writeto(_output_file, clobber=True)

        elif algorithm in 'gaussian':
            HDUl = pyfits.HDUList()
            HDUl.append(pyfits.PrimaryHDU(header))
            HDUl.append(pyfits.ImageHDU(data=m0, name='Gaussian_Peak'))
            HDUl.append(pyfits.ImageHDU(data=m1, name='Gaussian_Center',
                                        header=h1))
            HDUl.append(pyfits.ImageHDU(data=m2, name='Gaussian_STDDEV',
                                        header=h2))
            HDUl.writeto(_output_file, clobber=True)


class FitGaussian:
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
        self._g = None

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
        s = data[:, j, i]

        h = pyfits.getheader(self._filename)
        self._z = \
            (np.arange(s.size) - h['CRPIX3'] - 1) * h['CDELT3'] + h['CRVAL3']

        del data
        del h

        channel = np.arange(self._z.size)
        arg_max = (channel * s).sum() / s.sum()
        arg_max = round(arg_max, 0)
        arg_max = int(arg_max)
        arg_max = min(arg_max, 0)
        arg_max = max(arg_max, self._z.size - 1)

        amp = s[arg_max]
        avg = self._z[arg_max]

        fitter = fitting.LevMarLSQFitter()
        g = models.Gaussian1D(amplitude=amp, mean=avg, stddev=2.0)
        g = fitter(g, self._z, s)

        if  fitter.fit_info['ierr'] not in [1, 2, 3, 4]:
            return [np.nan, np.nan, np.nan]

        return [g.amplitude.value, g.mean.value, g.stddev.value]


class FitLorentzian:
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
        #self._g = None

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
        s = data[:, j, i]

        h = pyfits.getheader(self._filename)
        self._z = \
            (np.arange(s.size) - h['CRPIX3'] - 1) * h['CDELT3'] + h['CRVAL3']

        del data
        del h

        channel = np.arange(self._z.size)
        arg_max = (channel * s).sum() / s.sum()
        arg_max = round(arg_max, 0)
        arg_max = int(arg_max)
        arg_max = min(arg_max, 0)
        arg_max = max(arg_max, self._z.size - 1)

        amplitude = s[arg_max]
        x_0 = self._z[arg_max]

        fitter = fitting.LevMarLSQFitter()
        l = models.Lorentz1D(amplitude=amplitude, x_0=x_0, fwhm=5.0)
        l = fitter(l, self._z, s)

        if  fitter.fit_info['ierr'] not in [1, 2, 3, 4]:
            return [np.nan, np.nan, np.nan]

        return [l.amplitude.value, l.x_0.value, l.fwhm.value]


class DirectMeasure:
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
        s = data[:, j, i]

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

        return [flux, x_0, stddev]


if __name__ == '__main__':
    main()
