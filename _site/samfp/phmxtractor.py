#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
    Phase-map eXtractor
    by Bruno C Quint

    v1a - Phase extraction for Fabry-Perot.
    2014.04.16 15:45 - Created an exception for errors while trying to access
                       'CRPIX%' cards on cube's header.

    Todo
    ----
        - Add debug option to argparse
        - Add log-to-a-file option to argparse
        - Add multithread/multiprocess
        - Use astropy.ccdproc
        - Verify code
"""

from __future__ import absolute_import, division, print_function

import matplotlib
matplotlib.use('Qt5Agg')

from .tools import io, plots, version

import argparse
import astropy.io.fits as pyfits
import glob
import logging
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import multiprocessing
import numpy as np
import os
import time
import scipy
import sys

from astropy.modeling import models, fitting
from scipy import interpolate, signal

log = io.MyLogger(__name__)


def main():
    """Main method that runs the Phase-map Extraction."""

    # Parse arguments
    args = _parse_arguments()
    log.set_verbose(not args.quiet)
    log.set_debug(args.debug)

    # Start program
    start = time.time()
    log.info("")
    log.info("SAM-FP Tools: PHase-Map eXtractor")
    log.info("by Bruno Quint (bquint@ctio.noao.edu)")
    log.info("version {:s}".format(version.__str__))
    log.info("Starting program.")
    log.info("")

    log.info("Extracting phase-map from file: %s" % args.filename)
    log.info('')

    # Checking input data
    _check_dimensions(args.filename, log)

    # # Extracting phase-map
    phm = PhaseMap(
        args.filename,
        args.wavelength,
        correlation=args.correlation,
        show=args.show,
        verbose=not args.quiet,
        ref=args.ref,
        output=args.output
    )

    # Run!
    phm()

    # All done!
    end = time.time() - start
    log.info("Total time elapsed: %02d:%02d:%02d" %
             (end // 3600, end % 3600 // 60, end % 60))
    log.info("All done!\n")

    return
    # End of the main function


def _parse_arguments():
    """
    Method that parses the arguments given by the user via command line.

    Returns
    -------
        args (namespace) : a namespace with the arguments to be used by this
        script.
    """
    _about = "Extracts the phase-map from a fits file containing a data-cube."

    parser = argparse.ArgumentParser(description=_about)

    parser.add_argument('filename', type=str, help="Input data-cube name.")
    parser.add_argument('wavelength', type=float,
                        help="Wavelength in A of the strongest line "
                             "in the calibration cube.")

    parser.add_argument('-c', '--correlation', action='store_true',
                        help="Use correlation cube? true/[FALSE]")
    parser.add_argument('-d', '--debug', action='store_true',
                        help="Enable debug mode.")
    parser.add_argument('-o', '--output', type=str, default=None,
                        help="Name of the output phase-map file.")
    parser.add_argument('-q', '--quiet', action='store_true',
                        help="Run program quietly. true/[FALSE]")
    parser.add_argument('-r', '--ref', type=int, nargs=2, default=None,
                        help="Reference pixel for the correlation cube.")
    parser.add_argument('-s', '--show', action='store_true',
                        help="Show plots used in the process. true/[FALSE]")

    args = parser.parse_args()
    return args


def _check_dimensions(filename, log, dimensions=3, keyword='NAXIS'):
    """
    Method written to check the dimensions of the input fits data.

    Parameters
    ----------
        filename (str) : String containing path to the input filename.

        log (logging.Logger) : a logget for information

        dimensions (int) : Base number of dimensions for reference.

        keyword (str) : Header keyword that holds the number of axis
        (dimensions).
    """
    header = pyfits.getheader(filename)

    if keyword not in header:
        data = pyfits.getdata(filename)
        ndim = data.ndim
    else:
        ndim = header[keyword]

    if ndim is not dimensions:
        log.error("INVALID DATA: wrong number of dimensions."
                  "Leaving now!\n")
        sys.exit()
    else:
        return


class PhaseMap:

    """
    Class that holds the methods and sequences to perform phase-map extraction
    on a data-cube obtained with Fabry-Perot.

    Parameters
    ----------
        filename : str
            String that contains the path to the input data-cube.

        correlation : bool
            Use correlation cube? This is usefull in case that you have several
            lines in the data-cube or even if the data-cube has a low
            signal-to-noise ratio.

        show : bool
            Do you want the process to show plots? This is useful for
            debugging. If you know that your data is well behaved, you can
            leave this as false.

        verbose : bool
            Turn on verbose mode?

        output : str
            String that contains the path to the output phase-map.
    """
    loading = [' ', '-', '\\', '|', '/']

    def __init__(self, filename, wavelength, correlation=False, output=None,
                 ref=None, show=False, verbose=False):

        # Setting main configuration
        self.input_file = filename
        self.correlation = correlation
        self.output_file = output
        self.ref = ref
        self.show = show
        self.verbose = verbose
        self.wavelength = wavelength

        # Reading raw data
        self.data = pyfits.getdata(filename)
        self.header = pyfits.getheader(filename)

        # Reading data-cube configuration
        self.width = self.header['NAXIS1']
        self.height = self.header['NAXIS2']
        self.depth = self.header['NAXIS3']

        # Reading Z calibration for plotting
        self.z = self.get_calibration()

        try:
            self.units = self.header['CUNIT3']
        except KeyError:
            self.units = "channels"

        try:
            self.current_sampling = self.header['C3_3']
        except KeyError:
            self.current_sampling = 1.0


    def __call__(self):

        # Subtract continuum
        self.data = self.subtract_continuum(self.data, show=self.show)

        # Get the correlation cube
        if self.correlation:
            self.extract_from = self.use_correlation()
        else:
            self.extract_from = self.input_file

        # Measure the free-spectral-range
        self.free_spectral_range, self.fsr_channel = \
            self.get_free_spectral_range()

        # Get the center of the rings
        if self.ref is None:
            ref = self.find_reference_pixel()
            self.ref_x, self.ref_y = ref[:]

        self.ref_s = self.get_reference_spectrum(
            self.input_file, self.ref_x, self.ref_y, self.z, units=self.units,
            show=False)

        # # Calculate the FWHM
        self.fwhm = self.get_fwhm(self.z, self.ref_s, show=self.show)

        # # Calculate the finesse
        self.finesse = self.get_finesse()

        log.info("Ideal number of channels: %.1f channels"
                 % round(2 * self.finesse))
        log.info("Ideal sampling: %.1f %s / channel"
                 % (self.free_spectral_range / round(2 * self.finesse),
                    self.units))

        self.phase_map = self.extract_phase_map()
        self.save()

    def extract_phase_map(self):
        """
        Extract the phase-map.
        """
        now = time.time()

        # Reading data
        log.info("")
        log.info("Starting phase-map extraction.")
        log.info("Reading data from %s file" % self.extract_from)
        data = pyfits.getdata(self.extract_from)

        phase_map = np.argmax(data, axis=0).astype('float64')
        phase_map -= phase_map[self.ref_y, self.ref_x]
        phase_map *= self.current_sampling

        log.info("Done in %.2f seconds" % (time.time() - now))
        return phase_map

    def find_reference_pixel(self):
        """
        Read the reference pixel from header or find it.

        Returns
        -------
            ref_x (int) : X position of the center of the rings.
            ref_y (int) : Y position of the center of the rings.
        """
        log.info("")
        log.info("Finding reference pixel.")

        if ('PHMREFX' in self.header) and ('PHMREFY' in self.header):
            ref_x = self.header['PHMREFX']
            ref_y = self.header['PHMREFY']
            log.info("Found reference pixel found in header.")
            log.info("Using [%d, %d]" % (ref_x, ref_y))

        else:
            log.info("Reference pixel NOT found in header.")
            log.info("Trying to find the center of the rings.")
            ref_x, ref_y = self.find_rings_center(self.fsr_channel)

        return ref_x, ref_y

    def find_rings_center(self, fsr_channel, n_interactions=20):
        """
        Method used to find the center of the rings inside a FP data-cube by
        cutting it in two directions (XZ to find Y center and YZ to find X
        center), fitting a 2nd degree polynomium and get its extrema points.

        Parameters
        ----------
            fsr_channel (int) : free-spectral-range in number of channels
            n_interactions (int) : Number of interactions to find the center.

        Returns
        -------
            ref_x (int) : X position of the center of the rings.
            ref_y (int) : Y position of the center of the rings.
        """
        now = time.time()
        depth, height, width = self.data.shape

        # Choosing the points
        x = (np.linspace(0.05, 0.95, 500) * width).astype(int)
        y = (np.linspace(0.05, 0.95, 500) * height).astype(int)

        # First guess is that the reference pixel is at the center
        ref_x = self.header['NAXIS1'] // 2
        ref_y = self.header['NAXIS2'] // 2

        # Storing reference pixels for comparison between interactions
        log.info("Start center finding.")
        old_ref_x = ref_x
        old_ref_y = ref_y

        # Starting interactions
        for i in range(n_interactions):

            # Make sure my ref pixels are within the cube
            ref_y = max(ref_y, 0)
            ref_y = min(ref_y, height - 1)

            ref_x = max(ref_x, 0)
            ref_x = min(ref_x, width - 1)

            # Get a slice
            slice_in_x = self.data[:, ref_y, x]
            slice_in_y = self.data[:, y, ref_x]

            # Find the peaks
            p = multiprocessing.Pool(16)
            px = PeakFinder(slice_in_x)
            py = PeakFinder(slice_in_y)

            peaks_x = np.array(p.map(px, range(x.size)))
            peaks_y = np.array(p.map(py, range(y.size)))

            # Unwrap the FSR
            peaks_x = self.unwrap_fsr(peaks_x, fsr_channel, 'Running for X')
            peaks_y = self.unwrap_fsr(peaks_y, fsr_channel, 'Running for Y')

            # Not that it is fixed, I can fit the parabola
            px = scipy.polyfit(x, peaks_x, 2)
            py = scipy.polyfit(y, peaks_y, 2)

            ref_x = int(round(- px[1] / (2.0 * px[0])))
            ref_y = int(round(- py[1] / (2.0 * py[0])))

            # Selecting valid data
            error_x = np.abs(peaks_x - scipy.polyval(px, x))
            error_y = np.abs(peaks_y - scipy.polyval(py, y))

            if self.show:
                plt.title("Finding center of the rings")
                plt.clf()
                fig = plt.gcf()
                gs = gridspec.GridSpec(2, 1, height_ratios=[6, 2])

                ax1 = plt.subplot(gs[0])
                ax1.plot(x, peaks_x, 'b.', alpha=0.25)
                ax1.plot(x, scipy.polyval(px, x), 'b-', lw=2)
                ax1.axvline(ref_x, ls='--', c='blue', label='x')

                ax1.plot(y, peaks_y, 'r.', alpha=0.25)
                ax1.plot(y, scipy.polyval(py, y), 'r-', lw=2)
                ax1.axvline(ref_y, ls='--', c='red', label='y')

                ax1.legend(loc='best')
                ax1.grid()
                ax1.set_ylabel("Iteration number %d" % (i + 1))

                ax2 = plt.subplot(gs[1], sharex=ax1)
                ax2.plot(x, peaks_x - scipy.polyval(px, x), 'o', color='b',
                         alpha=0.25)
                ax2.plot(y, peaks_y - scipy.polyval(py, y), 'o', color='r',
                         alpha=0.25)

                fig.add_axes(ax1)
                fig.add_axes(ax2)

            # Measuring the error
            xl = np.diff(peaks_x)
            yl = np.diff(peaks_x)
            cond_x = np.where(error_x <= 3 * np.abs(np.median(xl[xl != 0])),
                              True, False)
            cond_y = np.where(error_y <= 3 * np.abs(np.median(yl[yl != 0])),
                              True, False)

            x = x[cond_x]
            y = y[cond_y]

            # Choosing when to stop
            if (abs(old_ref_x - ref_x) <= 2) and (abs(old_ref_y - ref_y) <= 2):

                try:

                    # If the cube was binned this will be useful
                    ref_x = (ref_x - self.header['CRPIX1'] + 1) * \
                            self.header['CDELT1'] + self.header['CRVAL1']

                    # If the cube was binned this will be useful
                    ref_y = (ref_y - self.header['CRPIX2']) * \
                            self.header['CDELT2'] + self.header['CRVAL2']

                except KeyError:
                    pass

                log.info("Rings center found at: [%d, %d]" % (ref_x, ref_y))
                log.info("Done in %.2f s" % (time.time() - now))

                if self.show:
                    plt.tight_layout()
                    plt.show()

                return ref_x, ref_y

            else:
                old_ref_x = ref_x
                old_ref_y = ref_y

            if self.show:
                plt.tight_layout()
                plt.show()

        # If my program gets here, it could not find the center.
        # So what?
        log.warning("Maximum number of interactions reached.")
        log.warning("Current center position at [%d, %d]" % (ref_x, ref_y))
        log.warning("Do you want to use these numbers?")

        reply = '.'
        while reply not in ' yn':
            reply = io.input('? ')
            if reply.lower() == 'n':
                log.warning('Ok then. Moving forward.')
                sys.exit()
            if reply.lower() == 'y':
                log.warning('Ok then. Moving forward.')
                return ref_x, ref_y

        log.warning("Do you want to continue? [Y,n]")
        reply = '.'
        while reply not in ' yn':
            reply = io.input('? ')
            if reply.lower() == 'n':
                log.warning('Ok then. Leaving now.')
                sys.exit()

        log.info("Then, enter the reference X in pixel:")
        log.info("Leave it empty to get it in the center of the image")
        reply = '.'
        while not reply.isdigit():
            reply = io.input('? ')
            if reply == '':
                reply = self.header['NAXIS1'] // 2
                break
        ref_x = int(reply)

        log.info("Then, enter the reference Y in pixels:")
        log.info("Leave it empty to get it in the center of the image")
        reply = '.'
        while not reply.isdigit():
            reply = io.input('? ')
            if reply == '':
                reply = self.header['NAXIS2'] // 2
                break
        ref_y = int(reply)

        # If the cube was binned this will be useful
        try:
            ref_x = (ref_x - self.header['CRPIX1']) \
                    * self.header['CDELT1'] + self.header['CRVAL1']
            ref_y = (ref_y - self.header['CRPIX2']) \
                    * self.header['CDELT2'] + self.header['CRVAL2']
        except KeyError:
            pass

        log.info("Done in %.2f s" % (time.time() - now))
        log.info("Using [%d, %d]." % (ref_x, ref_y))

        return ref_x, ref_y

    def get_calibration(self):
        """
        Return an array with the current calibration.
        """
        z = np.arange(self.depth)
        try:
            # The "+ 1" change from fortran like to c like indexing
            z = z - self.header['CRPIX3'] + 1
            z = z * self.header['C3_3']
            z = z + self.header['CRVAL3']
            log.debug('CRPIX3: %.2f' % self.header['CRPIX3'])
            log.debug('C3_3: %.2f' % self.header['C3_3'])
            log.debug('CRVAL3: %.2f' % self.header['CRVAL3'])

        except KeyError:
            log.warning("! Calibration in third axis not found.")
            log.warning("! I will ignore this step.")

        return z

    def get_finesse(self):
        """
        Assuming you have the Free-Spectral-Range in Z unit and that
        you have the FWHM in Z units as well, calculate the finesse by the
        expressions:

        .. math::
            F=\\frac{\\Delta z}{\\delta z}

        Returns
        -------
            finesse : float
        """
        finesse = self.free_spectral_range / self.fwhm

        if self.verbose:
            log.info("Finesse = %.1f" % finesse)

        return finesse

    def get_free_spectral_range(self):
        """
        A quick-and-dirty way to measure the free range in FP units.
        The method subtracts each frame of the data-cube from the
        first one. Then, it calculates the absolute value and collapse
        in X and Y. The FSR is where the resulting spectrum is minimum,
        excluding (of course), the first one.

        Returns
        -------
            fsr : float
                Free-spectral-range in BCV units.

            fsr_channel : int
                Free-spectral-range in channels.
        """
        log.info("Finding the free-spectral-range.")

        now = time.time()

        # First frame is the reference frame
        ref_frame = self.data[0, :, :]

        # Subtract all frames from the first frame
        data = self.data - ref_frame

        # Get the absolute value
        data = np.abs(data)

        # Sum over the spatial directions
        data = data.mean(axis=2)
        data = data.mean(axis=1)

        # Interpolate data
        s = interpolate.interp1d(self.z, data, kind='cubic')
        z = np.linspace(self.z[5], self.z[-1], 10000)

        # Find the free-spectral-range in z units
        fsr = np.abs(z[np.argmin(s(z))] - self.z[0])
        log.info('FSR = %.2f' % fsr)

        # Find the free-spectral-range in number of channels
        temp = self.z - z[np.argmin(s(z))]
        temp = np.abs(temp)
        fsr_c = np.argmin(temp)

        # Fix for python style
        fsr_c = fsr_c + 1
        log.info('FSR channel = %d' % fsr_c)

        # Plot to see how it goes
        if self.show:
            plots.free_spectral_range(self.z, data, s, fsr_c)

        # What if my cube has less than a FSR or could not find it?
        if fsr_c == 5:

            log.warning("FSR could not be found.")
            log.info("Do you want to continue? [Y,n]")

            reply = '.'
            while reply not in ' yn':
                reply = io.input('? ')
                if reply.lower() == 'n':
                    sys.exit()

            log.info("Then, enter a FSR in Z units (usually BCV):")
            reply = '.'
            while not reply.isdigit():
                reply = io.input('? ')
            fsr = float(reply)

            log.info("Then, enter a FSR in number of channels:")
            reply = '.'
            while not reply.isdigit():
                reply = io.input('? ')
            fsr_channel = int(reply)

        elif fsr_c == len(data):
            log.info("It seems that you scanned exactly over a FSR.")
            log.info("If not, check your data and phasemap_fit again.")

        # Calculate the sampling
        sampling = fsr / fsr_c

        log.info("FSR = %.1f %s" % (fsr, self.units))
        log.info("    = %d channels" % fsr_c)
        log.info("Sampling = %.1f %s / channel" % (sampling, self.units))
        log.info("Done in %.2f s" % (time.time() - now))

        return fsr, fsr_c

    @staticmethod
    def get_fwhm(z, s, show=False):
        """
        Returns the full-width-at-half-maximum using different models. These
        models can be displayed.

        Parameters
        ----------
            z (array like) : the abscissa of the reference spectrum containing
            the bcv values for each channel or the channel itself.

            s (array like) : the ordinate of the reference spectrum containing
            the intensity at each channel or at each bcv value.

            show (bool, optional) : display plots?

        Returns
        -------
            fwhm (float) : the full-width-at-half-maximum in units equal to z
            (either channel or bcv).
        """


        # Get statistics
        midpt = np.median(s)
        std = np.std(s)

        # Clear data
        p = np.percentile(s, 50.)
        s_ = s.copy()
        s_[s < p] = 0.

        # Find maxima avoiding the borders
        k = signal.general_gaussian(10, 1, 5)
        cc = signal.correlate(s_[5:-5], k, mode="same")
        arg_maxima = np.array([np.argmax(cc)]) + 5

        # arg_maxima = signal.argrelmax(s_[2:-2], order=5)[0]
        log.debug('Peaks found at: ' + np.array2string(arg_maxima,
                                                       separator=', '))

        fitter = fitting.LevMarLSQFitter()
        g_fwhm, l_fwhm, gauss = [], [], 0
        for (i, argm) in enumerate(arg_maxima):

            g = models.Gaussian1D(amplitude=s_[argm], mean=z[argm], stddev=1.)
            g_fit = fitter(g, z[1:-1], s_[1:-1])
            g_fwhm.append(g_fit.stddev * 2.355)

            l = models.Lorentz1D(amplitude=s_[argm], x_0=z[argm], fwhm=1.)
            l_fit = fitter(l, z[1:-1], s_[1:-1])
            l_fwhm.append(l_fit.fwhm)
        
            g_rms = np.sqrt(np.mean((s - g_fit(z)) ** 2))
            l_rms = np.sqrt(np.mean((s - l_fit(z)) ** 2))

            log.info("Peak at {:2d}".format(argm))
            log.info("gaussian fit rms: {:.2f}".format(g_rms))
            log.info("lorentzian fit rms: {:.2f}".format(l_rms))

            if g_rms > l_rms:
                gauss += 1
            else:
                gauss -= 1

        g_fwhm = np.mean(g_fwhm)
        l_fwhm = np.mean(l_fwhm)
        log.info("Gaussian fwhm: {:.2f}".format(g_fwhm))
        log.info("Lorentzian fwhm: {:.2f}".format(l_fwhm))

        if gauss > 0:
            fwhm_measured = g_fwhm
        elif gauss < 0:
            fwhm_measured = l_fwhm
        else:
            fwhm_measured = (g_fwhm + l_fwhm) * 0.5

        if show:

            z_ = np.linspace(z[0], z[-1], 1000)
            fig, axs = plt.subplots(2, 1, sharex=True)
            axs[0].plot(z, s, 'ko')
            axs[0].plot(z[5:-5], cc / cc.max() * s_.max(), 'y-', label='Cross-correlation')
            axs[0].grid()

            if len(arg_maxima) > 0:

                axs[0].plot(z_, g_fit(z_), 'b-')
                axs[0].plot(z_, l_fit(z_), 'r--')
                axs[0].legend(loc='best')
                axs[0].set_ylabel('Normalized spectrum')

                for amax in arg_maxima:
                    axs[0].axvline(z[amax], c='k', ls='--', alpha=0.5)

                # Display the errors
                axs[1].plot(z, s - g_fit(z), 'bx', alpha=0.5, label='Error - Gaussian Fit')
                axs[1].plot(z, s - l_fit(z), 'ro', alpha=0.5, label='Error - Lorentzian Fit')
                axs[1].set_ylabel('Fir Errors [adu]')
                axs[1].set_xlabel('z [bcv]')
                axs[1].legend(loc='best')
                axs[1].grid()

            plt.tight_layout()
            plt.show()

        return fwhm_measured

    @staticmethod
    def get_reference_spectrum(input_file, x, y, z, units='--', show=False):
        """
        Get the reference spectrum.
        """
        from scipy.stats import mode

        ref_s = pyfits.getdata(input_file)[:, y, x]
        ref_s /= ref_s.max()  # Normalize
        ref_s -= ref_s.mean()  # Remove mean to avoid triangular shape
        ref_s -= mode(ref_s)[0]  # Try to put zero on zero

        if show:
            plt.figure()
            plt.title("Reference Spectrum")
            plt.plot(z, ref_s, 'ko-', label="Reference spectrum")
            plt.grid()
            plt.xlabel("z [%s]" % units)
            plt.tight_layout()
            plt.show()

        return ref_s

    def unwrap_fsr(self, peaks, fsr_channel, running_for=None):
        """
        Use clusters of data to identify regions that are wrapped and
        unwrap it using the fsr in number of channels.

        Parameters
        ----------
        peaks (numpy.ndarray) : 1D array containing the peaks with more than a
            FSR.
        fsr_channel (int) : the FSR in number of channels.

        Returns
        -------
        peaks (numpy.ndarray) : 1D array containing the peaks unwrapped.

        To Do: Test with more than 1 FSR.
        """

        indexes = np.argsort(peaks)
        sorted_peaks = np.sort(peaks)
        diff_sorted_peaks = np.diff(sorted_peaks)
        temp = np.abs(diff_sorted_peaks)

        where = np.abs(temp - np.median(temp)) < np.std(temp)
        temp[where] = 0
        split_indexes = signal.argrelmax(temp)[0]

        split_y_indexes = np.split(indexes, split_indexes + 1)
        for (i, idx) in enumerate(split_y_indexes):
            peaks[idx] -= fsr_channel * i

        return peaks

    def use_correlation(self):
        """
        Use correlation data-cube.
        """
        log.info("A correlation cube will be used.")
        log.info("Looking for an existing correlation data-cube in the current "
                 "folder.")

        candidates = glob.glob("*.fits")

        corr_cube = None
        for candidate in candidates:
            if 'CORRFROM' in pyfits.getheader(candidate):
                if pyfits.getheader(candidate)['CORRFROM'] == self.input_file:
                    log.info("Correlation cube to be used: %s" % candidate)
                    return candidate

        if corr_cube is None:
            log.info("Correlation cube not found. Creating a new one.")
            data = pyfits.getdata(self.input_file)
            corr_cube = np.empty_like(data)

            x = np.arange(self.width)
            y = np.arange(self.height)
            x, y = np.meshgrid(x, y)
            x, y = np.ravel(x), np.ravel(y)

            for i in range(x.size):
                s = data[:, y[i], x[i]]
                s = s / s.max()  # Normalize
                s = s - s.mean()  # Remove mean to avoid triangular shape
                s = np.correlate(s, self.ref_s, mode='same')
                corr_cube[:, y[i], x[i]] = s

                temp = ((i + 1) * 100.00 / x.size)
                sys.stdout.write('\r %2d%% ' % temp)
                sys.stdout.write(self.loading[int(temp * 10 % 5)])
                sys.stdout.flush()

            log.info("Done.")
            corr_name = os.path.splitext(self.input_file)[0] + '--corrcube.fits'
            log.info("Saving correlation cube to %s" % corr_name)

            corr_hdr = self.header.copy()
            corr_hdr.set('CORRFROM', self.input_file, 'Cube used for corrcube.')
            corr_hdr.set('', '', before='CORRFROM')
            corr_hdr.set('', '--- Correlation cube ---', before='CORRFROM')

            pyfits.writeto(corr_name, corr_cube, corr_hdr, overwrite=True)
            del corr_hdr
            del corr_cube

            return corr_name

    def save(self):

        # Getting the input information to work on in
        f = os.path.splitext(self.input_file)[0]
        h = self.header.copy()

        fsr = round(self.free_spectral_range, 2)

        h = pyfits.Header()

        # Setting what is the reference pixels
        h.set('PHMREFX', value=self.ref_x, comment='Rings center - x')
        h.set('PHMREFY', value=self.ref_y, comment='Rings center - y',
              after='PHMREFX')

        h.add_blank('', before='PHMREFX')
        h.add_blank('--- PHM Xtractor ---', before='PHMREFX')

        # Store information gathered
        h.set('PHMTYPE', value='observed', comment='', after='PHMREFY')
        h.set('PHMREFF', value=self.input_file, comment='Original file',
              after='PHMTYPE')
        h.set('PHMWCAL', value=self.wavelength,
              comment='Wavelength for calibration', after='PHMREFF')
        h.set('PHM_FSR', value=fsr, comment='FSR in %s units' % self.units,
              after='PHMWCAL')
        h.set('PHMUNIT', value=self.units, comment='Units for z and FSR.',
              after='PHM_FSR')
        h.set('PHMSAMP', value=self.current_sampling,
              comment="Sampling per channel", after='PHMUNIT')

        self.phase_map = self.phase_map - self.phase_map[
            self.ref_y, self.ref_x]

        try:
            del (h['CRPIX3'], h['CRVAL3'], h['C3_3'], h['CDELT3'])
        except KeyError:
            pass

        filename = io.safe_save(f + "--obs_phmap.fits", overwrite=True,
                             verbose=self.verbose)
        log.info("Saving observed phase-map to file: %s" % filename)
        pyfits.writeto(filename, self.phase_map, h, overwrite=True)

        filename = io.safe_save(f + "--ref_spec.fits", overwrite=True,
                             verbose=self.verbose)
        log.info("Saving reference spectrum to file: %s" % filename)
        pyfits.writeto(filename, self.ref_s, h, overwrite=True)

        return

    @staticmethod
    def subtract_continuum(data, show=False):

        ordered_data = np.sort(data, axis=0)
        continuum = np.median(ordered_data[:5], axis=0)
        del ordered_data

        #if show:
        #    plots.show_image(continuum, 'viridis', "Cube continuum")

        data -= continuum
        return data


class PeakFinder:

    def __init__(self, data):
        assert data.ndim == 2
        self.data = data

    def __call__(self, i):
        data = self.data[:, i]
        data -= np.median(data)
        data = np.where(data > 0.70 * np.max(data), data, 0)
        n = int(data.shape[0] * 0.2)
        peaks = signal.argrelmax(data, axis=0, order=n)[0]
        peak = np.min(peaks)

        return peak

