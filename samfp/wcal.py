#!/usr/bin/env python2
# -*- coding: utf8 -*-
"""
    Wavelength Calibration

    This script calculates the wavelength calibration using a Terminal Interface
    with the User.
"""
from __future__ import division, print_function

import argparse
import astropy.io.fits as pyfits
import logging as log
import numpy as np

from scipy import signal

__author__ = 'Bruno Quint'


class WavelengthCalibration:
    """
    Wavelength calibration

    This class holds methods and properties needed to perform a wavelength
    calibration on a phase-corrected data-cube. For that, it will use
    theoretical equations and assume that the FP has a nominal gap size.
    """
    def __call__(self, filename, output=None):
        """
        One this class is called, the 'main' method is invoked.
        Please, refer to its documentation for details.

        Parameters
        ----------
        filename : str
            Input filename.
        output : str
            Output filename (optional).
        """
        self.main(filename, output)
        return

    def __init__(self, verbose=False, debug=False):
        """
        Class constructor. For now, it will only receive the paramaters
        related to feedback that is given to the user via terminal.

        Parameters
        ----------
        verbose : bool
        debug : bool
        """
        self._log = log
        print(self._log.getLogger().getEffectiveLevel())
        self.set_verbose(verbose)
        print(self._log.getLogger().getEffectiveLevel())
        self.set_debug(debug)
        print(self._log.getLogger().getEffectiveLevel())

        return

    @staticmethod
    def center_peak(data, center):
        """
        Based on the most probable center position, rolls the line so it lies
        in the center of the data-cube.

        Parameters
        ----------
        data : numpy.ndarray
            The data-cube represented in a numpy.ndarray form.
        center : int
            The argument of the channel that contains the most probable
            center of the strongest feature.
        """
        cube_center = data.shape[0] // 2
        shift_size = cube_center - center
        data = np.roll(data, shift_size, axis=0)
        return data

    def debug(self, message):
        """Print a debug message using the log system."""
        self._log.debug(message)
        return

    def find_current_peak_position(self, data):
        """
        Finds the current average peak position.

        Parameters
        ----------
            data : numpy.ndarray
            A phase-corrected datacube.

        Returns
        -------
            peak_position : int
            The argument of the highest local maximum.
        """
        self.info('Finding current peak position.')
        data = data.sum(axis=2)
        data = data.sum(axis=1)
        data = np.where(data < 0.75 * data.max(), 0, data)
        peaks = signal.argrelmax(data, axis=0, order=5)[0]
        self.info('Encountered {:d} peaks: '.format(len(peaks)))

        peaks_values = data[peaks]
        max_peaks_arg = np.argmax(peaks_values)
        peak = peaks[max_peaks_arg]

        return peak

    def get_central_wavelength(self, header=None, key='FP_WOBS'):
        """
        Read the central wavelength from a header or from the user input.

        Parameters
        ----------
            header : astropy.io.fits.Header
                A FITS header.
            key : str
                A key that, in theory, has the observed wavelength.

        Returns
        -------
            central_wavelength : float
                Systemic central wavelength in meters.
        """

        try:
            central_wavelength = float(header[key])
        except KeyError:
            self.warn('%s card was not found in the header.' % key)
            central_wavelength = input(' Please, enter the systemic observed '
                                       'wavelength: \n >')
        except TypeError:
            self.warn(
                'Header was not passed to "WCal.get_central_wavelength" method'
            )
            central_wavelength = input(
                ' Please, enter the systemic observed wavelength: \n > '
            )
            central_wavelength = float(central_wavelength)

        return central_wavelength * 1e-10

    def get_logger(self):
        """Create and return a customized logger object.

        :return log: the logger object.
        :rtype log: log.Logger
        """
        lf = MyLogFormatter()

        ch = self.log.StreamHandler()
        ch.setFormatter(lf)

        self.log.captureWarnings(True)
        log = self.log.getLogger("phasemap_fit")
        log.addHandler(ch)

        return log

    def get_wavelength_step(self, w_central, header=None, key_gap_size='FP_GAP',
                            key_zfsr='PHMFSR', key_z_step='CDELT3'):
        """
        Calculates the wavelength step between channels.

        :return w_step: wavelength increment beween channels.
        :rtype w_step: float
        """
        try:
            gap_size = header[key_gap_size]
        except KeyError:
            self.warn('%s card was not found in the header.' % key_gap_size)
            gap_size = input('Please, enter the FP nominal gap size in microns:'
                             '\n >  ')
        except TypeError:
            self.warn('Header was not passed to "WCal.get_wavelength_step"'
                         ' method')
            gap_size = input('Please, enter the FP nominal gap size in microns:'
                             '\n >  ')

        try:
            z_fsr = header[key_zfsr]
        except KeyError:
            self.warn('%s card was not found in the header.' % key_zfsr)
            z_fsr = input('Please, enter the Free-Spectral-Range in bcv:'
                          '\n > ')
        except TypeError:
            log.warning('Header was not passed to "WCal.get_wavelength_step"'
                        ' method')
            z_fsr = input('Please, enter the Free-Spectral-Range in bcv:'
                          '\n >  ')

        try:
            z_step = header[key_z_step]
        except KeyError:
            log.warning('%s card was not found in the header.' % key_z_step)
            z_step = input('Please, enter the step between channels in bcv'
                           '\n >  ')
        except TypeError:
            log.warning('Header was not passed to "WCal.get_wavelength_step"'
                        ' method')
            z_step = input('Please, enter the step between channels in bcv'
                           '\n >  ')

        gap_size = gap_size * 1e-6
        self.info('Gap size e = {:.1f} um'.format(gap_size * 1e6))

        w_order = 2 * gap_size / w_central
        self.info('Interference order p({:.02f}) = {:.2f}'.format(
            w_central * 1e10, w_order))

        self.info('Z Free-Spectral-Range = {:.02f} bcv'.format(z_fsr))
        w_fsr = w_central / (w_order * (1 + 1 / w_order ** 2))
        self.info('W Free-Spectral-Range = {:.02f} A'.format(w_fsr * 1e10))

        w_step = w_fsr / z_fsr * z_step
        self.info('Queesgate constant = {:.02f} A / bcv'.format(w_fsr / z_fsr * 1e10))
        self.info('Step = {:.02f} A / channel'.format(w_step * 1e10))

        return w_step

    def info(self, message):
        """Print an info message using the log system."""
        self._log.info(message)
        return

    def load_data(self, input_filename):
        """Load the input data and header."""

        self.info('Loading %s' % input_filename)
        data = pyfits.getdata(input_filename)
        hdr = pyfits.getheader(input_filename)
        self.info('Done')

        return data, hdr

    def main(self, filename, output=None):
        """
        This is the main method that can be called via .main() or
        via (). It colapses part of the data-cube, finds the most
        strong spectral signal and put it at the center of
        the data-cube. Then, needs the numerical parameters
        to calculate the proper wavelength calibration.

        Parameters
        ----------
        filename : str
            Input filename.

        output : str
            Output filename (optional).
        """
        from os.path import exists
        from astropy.io.fits import getdata, getheader, writeto

        # Make sure that input file exists and can be read ---
        if not exists(filename):
            raise(IOError, 'Input file not found: {:s}'.format(filename))

        # Load data ---
        self.info('Loading file: {:s}'.format(filename))
        data = getdata(filename)
        hdr = getheader(filename)

        # Find strongest signal ---
        self.info('Find current peak position...')
        current_peak_position = self.find_current_peak_position(data)

        # Roll cube to put the peak at the center of the cube ---
        self.info('Rolling the cube to put peak at the center...')
        data = self.center_peak(data, current_peak_position)

        # Get systemic wavelength ---
        self.info('Getting systemic wavelength...')
        w_center = self.get_central_wavelength(hdr)

        # Get increment wavelength ---
        self.info('Getting increment wavelength...')
        w_step = self.get_wavelength_step(w_center, hdr)

        # Update header ---
        hdr = self.update_header(hdr, w_center, w_step)

        # Write file ---
        if output is None:
            output = filename.replace('.fits', '.wcal.fits')

        self.info('Writing output file: {:s}'.format(output))

        # Wrap-up to make sure that writeto will be available in the next
        # versions
        try:
            writeto(output, data, hdr, overwrite=True)
        except TypeError:
            writeto(output, data, hdr, clobber=True)


        # Leaving the program ---
        self.info('Total ellapsed time: \n'
                  'All done.\n')

        return

    def print_header(self):
        """
        Simply print a header for the script.
        """
        msg = "\n " \
              " Data-Cube Wavelength Calibration\n" \
              " by Bruno C. Quint (bquint@ctio.noao.edu)\n"
        self.info(msg)
        return

    def update_header(self, header, w_center, w_step):
        """
        Update the header so it contains the wavelength calibration.
        This part still have to be updated to follow the 4.0 version
        of the FITS standards (see link bellow).

        http://fits.gsfc.nasa.gov/standard40/fits_standard40draft1.pdf

        Parameters
        ----------
        header : astropy.io.fits.Header
            Header of the data-cube that will be updated.
        w_center : float
            Wavelength at the center of the data-cube.
        w_step : float
            Wavelength increment between channels.

        Returns
        -------
        header : astropy.io.fits.Header
            An updated header.
        """
        header.add_blank(before=-1)
        header.add_blank('--- Wavelength Calibration ---', before=-1)
        header.set('CRPIX3', int(header['NAXIS3']) / 2 + 1, before=-1)
        header.set('CRVAL3', w_center * 1e10, before=-1)
        header.set('CDELT3', w_step * 1e10, before=-1)
        header.set('CUNIT3', 'angstrom', before=-1)
        header.set('RESTWAV', w_center * 1e10, before=-1)

        return header

    def set_log_level(self, level):
        """
        Set the internal logger level.

        :param level: logger level.
        :type level: logger.DEBUG|logger.WARNING|logger.CRITICAL
        """
        self.log.setLevel(level)

    def set_debug(self, debug):
        """
        Turn on debug mode.

        Parameter
        ---------
            debug : bool
        """
        print(debug)
        if debug:
            self._log.basicConfig(level=10, format='%(message)s')
        self.debug('Debug mode ON.')

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
        return

    def warn(self, message):
        """Print a warning message using the log system."""
        self._log.warning(message)


class MyLogFormatter(log.Formatter):
    err_fmt = "ERROR: %(msg)s"
    dbg_fmt = " DBG: %(module)s: %(lineno)d: %(msg)s"
    info_fmt = " %(msg)s"
    warn_fmt = " %(msg)s"

    def __init__(self, fmt="%(levelno)s: %(msg)s"):
        log.Formatter.__init__(self, fmt)

    def format(self, record):

        # Save the original format configured by the user
        # when the logger formatter was instantiated
        format_orig = self._fmt

        # Replace the original format with one customized by log level
        if record.levelno == log.DEBUG:
            self._fmt = MyLogFormatter.dbg_fmt

        elif record.levelno == log.INFO:
            self._fmt = MyLogFormatter.info_fmt

        elif record.levelno == log.ERROR:
            self._fmt = MyLogFormatter.err_fmt

        elif record.levelno == log.WARNING:
            self._fmt = MyLogFormatter.warn_fmt

        # Call the original formatter class to do the grunt work
        result = log.Formatter.format(self, record)

        # Restore the original format configured by the user
        self._fmt = format_orig

        return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Fits an existing phase-map."
    )

    parser.add_argument(
        'filename', type=str,
        help="Input phase-map name."
    )
    parser.add_argument(
        '-D', '--debug', action='store_true',
        help="Run program in debug mode."
    )
    parser.add_argument(
        '-o', '--output', type=str, default=None,
        help="Name of the output phase-map file."
    )
    parser.add_argument(
        '-q', '--quiet', action='store_true',
        help="Run program quietly."
    )

    args = parser.parse_args()

    wcal = WavelengthCalibration(verbose=not args.quiet, debug=args.debug)
    wcal(args.filename, output=args.output)
