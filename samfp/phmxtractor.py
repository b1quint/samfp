#!/usr/bin/env python2
# -*- coding: utf8 -*-
"""
    Phase-map Xtractor
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

from __future__ import division, print_function

import argparse
import astropy.io.fits as pyfits
import logging
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import time
import scipy
import scipy.interpolate as interpolate
import sys

from scipy import signal
from scipy import ndimage
from multiprocessing import Pool

from sklearn.cluster import MeanShift

log = logging.getLogger('phasemap_extractor')


def main():
    """
    Main method that runs the Phase-map Extraction.

    """

    # Parse arguments ---------------------------------------------------------
    parser = argparse.ArgumentParser(
        description="Extracts the phase-map from a fits file containing a "
                    "data-cube."
    )
    parser.add_argument(
        '-c', '--correlation', action='store_true',
        help="Use correlation cube? true/[FALSE]"
    )
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help="Enable debug mode."
    )
    parser.add_argument(
        'filename', type=str, help="Input data-cube name."
    )
    parser.add_argument(
        '-o', '--output', type=str, default=None,
        help="Name of the output phase-map file."
    )
    parser.add_argument(
        '-q', '--quiet', action='store_true',
        help="Run program quietly. true/[FALSE]"
    )
    parser.add_argument(
        '-r', '--ref', type=int, nargs=2, default=None,
        help="Reference pixel for the correlation cube."
    )
    parser.add_argument(
        '-s', '--show', action='store_true',
        help="Show plots used in the process. true/[FALSE]"
    )
    args = parser.parse_args()

    if args.quiet:
        log.setLevel(logging.NOTSET)
    else:
        log.setLevel(logging.INFO)

    if args.debug:
        log.setLevel(logging.DEBUG)

    # Starting program ---
    start = time.time()
    v = not args.quiet

    log.info("\n Phase-Map Extractor")
    log.info("by Bruno Quint & Fabricio Ferrari")
    log.info("version 0.1c - May 2014")
    log.info("Extracting phase-map from file: %s" % args.filename)

    # Checking input data -----------------------------------------------------
    log.info("Checking data-cube for phase-correction.")
    check_dimensions(args.filename)

    # Extracting phase-map -----------------------------
    PhaseMapFP(
        args.filename, correlation=args.correlation, show=args.show,
        verbose=v, ref=args.ref, output=args.output
    )

    # All done! ---------------------------------------------------------------
    end = time.time() - start
    log.info("\nTotal time elapsed: %02d:%02d:%02d" %
             (end // 3600, end % 3600 // 60, end % 60))
    log.info("All done!\n")

    return


def check_dimensions(filename, dimensions=3, keyword='NAXIS'):
    """
    Method written to check the dimensions of the input fits data.

    Parameters
    ----------
        filename : str
            String containing path to the input filename.

        dimensions : int
            Base number of dimensions for reference.

        keyword : str
            Header keyword that holds the number of axis (dimensions).
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


def safe_save(name, extension=None, overwrite=False, verbose=False):
    """
    This is a generic method used to check if a file called 'name' already
    exists. If so, it starts some interaction with the user.

    @param name: the name of the file that will be written in the future.

    @keyword extension: check if the file has the following extension. If not,
    it fills for the user. Defaults is None. An example would be
    extension='.fits'.

    @keyword overwrite: if False, this method will interact with the user to
    ask if 'name' file shall be overwritten or if a new name will be given. If
    True, 'name' file is automatically overwritten.

    @keyword verbose: force verbose mode on even when overwrite is automatic.

    v1.0.2 - added 'extension' keyword.
    v1.0.1 - added 'overwrite' keyword.
           - added 'verbose' keyword.
    """
    import os

    if os.path.splitext(name)[1] != extension and extension is not None:
        name = name + extension

    v = False if (overwrite is True) else True
    if v:
        log.info('\nWriting to output file "%s"' % name)

    while os.path.exists(name):

        if overwrite in ['y', 'Y', True]:
            if v or verbose:
                log.info(" Overwriting %s file." % name)
            os.remove(name)

        elif overwrite in ['', 'n', 'N', False]:
            name = input("Please, enter a new filename:\n > ")
            if os.path.splitext(name)[1] != extension and extension is not None:
                name = name + extension

        elif overwrite in ['q']:
            if v:
                log.info("Exiting program.")
            sys.exit()

        else:
            overwrite = input(" '%s' file exist. Overwrite? (y/[n])" % name)
            if v:
                log.info("Writing data-cube to %s" % name)

    return name


class MyLogFormatter(logging.Formatter):
    err_fmt = "ERROR: %(msg)s"
    dbg_fmt = " DBG: %(module)s: %(lineno)d: %(msg)s"
    info_fmt = " %(msg)s"
    warn_fmt = " %(msg)s"

    def __init__(self, fmt="%(levelno)s: %(msg)s"):
        logging.Formatter.__init__(self, fmt)

    def format(self, record):

        # Save the original format configured by the user
        # when the logger formatter was instantiated
        format_orig = self._fmt

        # Replace the original format with one customized by logging level
        if record.levelno == logging.DEBUG:
            self._fmt = MyLogFormatter.dbg_fmt

        elif record.levelno == logging.INFO:
            self._fmt = MyLogFormatter.info_fmt

        elif record.levelno == logging.ERROR:
            self._fmt = MyLogFormatter.err_fmt

        elif record.levelno == logging.WARNING:
            self._fmt = MyLogFormatter.warn_fmt

        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)

        # Restore the original format configured by the user
        self._fmt = format_orig

        return result


class PhaseMap:
    def __init__(self, filename, **config):

        # Setting main configuration ------------------------------------------
        self.input_file = filename
        self.output_file = config['output']
        self.config = config
        self.verbose = config['verbose']

        if 'show' in config:
            self.show = config['show']
        else:
            self.show = False

        self.loading = [' ', '-', '\\', '|', '/']

        # Reading raw data ----------------------------------------------------
        log.info("  Loading data.")
        self.data = pyfits.getdata(filename)
        self.header = pyfits.getheader(filename)
        log.info("  Done.")

        # Reading data-cube configuration -------------------------------------
        self.width = self.header['NAXIS1']
        self.height = self.header['NAXIS2']
        self.depth = self.header['NAXIS3']

        # Reading Z calibration for plotting ----------------------------------
        self.z = self.get_calibration()

        try:
            self.units = self.header['CUNIT3']
        except KeyError:
            self.units = "channels"

        try:
            self.sample = self.header['C3_3']
        except KeyError:
            self.sample = 1.0

        return

    def extract_phase_map(self):
        """
        Extract the phase-map.
        """
        from astropy.io.fits import getdata
        from numpy import argmax

        log.info("\n  Starting phase-map extraction.")
        log.info("  Reading data from %s file" % self.extract_from)
        data = getdata(self.extract_from)

        phase_map = argmax(data, axis=0)
        phase_map = phase_map - phase_map[self.ref_y, self.ref_x]
        phase_map = phase_map * self.sample
        return phase_map

    def find_reference_pixel(self):
        """
        Read the reference pixel from header or find it.
        """
        if ('PHMREFX' in self.header) and ('PHMREFY' in self.header):
            log.info(" \n  Found reference pixel in header.")
            ref_x = self.header['PHMREFX']
            ref_y = self.header['PHMREFY']
            log.info("  Using [%d, %d]" % (self.ref_x, self.ref_y))
        else:
            log.info(" \n  Reference pixel NOT in header.")

            answer = '.'
            while answer.lower() not in ' yn':
                answer = raw_input("? Use central pixel? [Y, n]\n? ")

            if answer.lower() in ' y':
                ref_x = self.width // 2
                ref_y = self.height // 2
            else:
                ref_x = int(raw_input("? Please, enter reference X: "))
                ref_y = int(raw_input("? Please, enter reference Y: "))

            log.info("  Using [%d, %d]" % (ref_x, ref_y))

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
            log.info("! Calibration in third axis not found.")
            log.info("! I will ignore this step.")

        return z

    def get_fwhm(self):
        """
        Returns the full-width-at-half-maximum.
        """

        # TODO Add an option to choose wheter to use gauss FWHM or measured FWHM

        from scipy.optimize import leastsq
        from scipy.stats import mode

        try:
            fsr = self.free_spectral_range / self.header['CDELT3']
        except KeyError:
            log.info(" WARNING: Z-Calibration not found!")
            fsr = self.free_spectral_range

        fsr = int(abs(fsr))
        z = self.z[:fsr]
        s = self.ref_s[:fsr]
        s = s - mode(s)[0]

        zz = np.linspace(z[0], z[-1], 1000)
        ss = interpolate.interp1d(z, s, kind='cubic')
        sss = ss(zz) - ss(zz).max() / 2

        fit_func = lambda p, x: p[0] * np.exp(-(x - p[1]) ** 2 / (2 * p[2] ** 2))
        err_func = lambda p, x, y: y - fit_func(p, x)
        pars = [sss.max(), zz[sss.argmax()], 10]
        pars, _ = leastsq(err_func, pars, args=(zz, ss(zz)))
        fwhm_gauss = 2.35482 * pars[2]

        zzz = zz[sss > 0]
        fwhm_measured = zzz.ptp()

        if self.show:
            plt.figure()
            plt.title("Measure the FWHM")
            plt.plot(z, s, 'bo')
            plt.plot(zz, ss(zz), 'b-', lw=2)
            plt.plot(zz, sss, 'r-', lw=2, alpha=0.3)
            plt.plot(zz, fit_func(pars, zz), 'g-', lw=2, alpha=0.3)
            plt.axvline(pars[1] - fwhm_gauss / 2, ls='--', c='green', lw=2)
            plt.axvline(pars[1] + fwhm_gauss / 2, ls='--', c='green', lw=2,
                        label='Gauss Fit = %.1f %s' % (fwhm_gauss, self.units))
            plt.axvline(zz[np.argmax(ss(zz))] + fwhm_measured / 2, ls='--', c='red', lw=2)
            plt.axvline(zz[np.argmax(ss(zz))] - fwhm_measured / 2, ls='--', c='red', lw=2,
                        label='Definition = %.1f %s' % (fwhm_measured, self.units))
            plt.legend(loc='best')
            plt.grid()
            plt.tight_layout()
            plt.show()

        if self.verbose:
            log.info("")
            log.info(" Measured FWHM = %.2f %s" % (fwhm_measured, self.units))
            log.info(" Gauss-fit FWHM = %.2f %s " % (fwhm_gauss, self.units))
            log.info(" Using the measured FWHM for further calculations.")

        return fwhm_measured

    def get_reference_spectrum(self):
        """
        Get the reference spectrum.
        """
        from scipy.stats import mode

        ref_s = pyfits.getdata(self.input_file)[:, self.ref_y, self.ref_x]
        ref_s = ref_s / ref_s.max()  # Normalize
        ref_s = ref_s - ref_s.mean()  # Remove mean to avoid triangular shape
        ref_s = ref_s - mode(ref_s)[0]  # Try to put zero on zero

        if self.show:
            plt.figure()
            plt.title("Reference Spectrum")
            plt.plot(self.z, ref_s, 'ko-', label="Reference spectrum")
            plt.grid()
            plt.xlabel("z [%s]" % self.units)
            plt.tight_layout()
            plt.show()

        return ref_s

    def use_correlation(self):
        """
        Use correlation data-cube.
        """
        import numpy

        from astropy.io.fits import getdata, getheader, writeto
        from glob import glob
        from os.path import splitext
        from sys import stdout

        log.info("\n A correlation cube will be used.")
        log.info(" Looking for an existing correlation data-cube in the current folder.")
        candidates = glob("*.fits")

        corr_cube = None
        for candidate in candidates:
            if 'CORRFROM' in getheader(candidate):
                if getheader(candidate)['CORRFROM'] == self.input_file:
                    log.info(" Correlation cube to be used: %s" % candidate)
                    return candidate

        if corr_cube is None:
            log.info(" Correlation cube not found. Creating a new one.")
            data = getdata(self.input_file)
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
                stdout.write('\r %2d%% ' % temp)
                stdout.write(self.loading[int(temp * 10 % 5)])
                stdout.flush()

            log.info(" Done.")
            corr_name = splitext(self.input_file)[0] + '--corrcube.fits'
            log.info(" Saving correlation cube to %s" % corr_name)

            corr_hdr = self.header.copy()
            corr_hdr.set('CORRFROM', self.input_file, 'Cube used for corrcube.')
            corr_hdr.set('', '', before='CORRFROM')
            corr_hdr.set('', '--- Correlation cube ---', before='CORRFROM')

            writeto(corr_name, corr_cube, corr_hdr, clobber=True)
            del corr_hdr
            del corr_cube

            return corr_name

    def save(self):
        """
        Save files.
        """
        from astropy.io.fits import writeto
        from os.path import splitext

        v = self.verbose
        f = splitext(self.input_file)[0]
        h = self.header.copy()
        h['PHMREFX'] = self.ref_x
        h.set('PHMREFY', self.ref_y)
        h.set('', '', before='PHMREFX')
        h.set('', '--- PHM Xtractor ---', before='PHMREFX')

        h.set('PHMREFF', self.input_file, 'Original file')
        h.set('PHMTYPE', 'observed')
        h.set('PHMUNIT', self.units)
        h.set('PHMSAMP', self.sample)

        if self.output_file is None:
            filename = safe_save(f + "--obs_phmap.fits", overwrite=True, verbose=v)
            log.info(" Saving observed phase-map to file: %s" % filename)
            writeto(filename, self.phase_map, h, clobber=True)

            # TODO Fix refspec file's header to keep calibration
            filename = safe_save(f + "--ref_spec.fits", overwrite=True, verbose=v)
            log.info(" Saving reference spectrum to file: %s" % filename)
            writeto(filename, self.ref_s, h, clobber=True)

        else:
            f = splitext(self.output_file)[0]
            filename = safe_save(f + "--obs_phmap.fits", overwrite=True, verbose=v)
            log.info(" Saving observed phase-map to file: %s" % filename)
            writeto(filename, self.phase_map, h, clobber=True)

            # TODO Fix refspec file's header to keep calibration
            filename = safe_save(f + "--ref_spec.fits", overwrite=True, verbose=v)
            log.info(" Saving reference spectrum to file: %s" % filename)
            writeto(filename, self.ref_s, h, clobber=True)

        return


class PhaseMapFP(PhaseMap):
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

    def __init__(self, filename, correlation=False, show=False,
                 verbose=False, ref=None, output=None):

        PhaseMap.__init__(self, filename, correlation=correlation,
                          show=show, verbose=verbose, output=output)

        # This is a Fabry-Perot data-cube. Let's make that clear to the user
        if self.verbose:
            log.info("\n Extracting phase-map from a Fabry-Perot data-cube.")

        # Measure the free-spectral-range --------------------------------------
        fsr = self.get_free_spectral_range()
        self.free_spectral_range, self.fsr_channel = fsr

        # Getting reference spectrum -------------------------------------------
        if ref is None:
            ref = self.find_reference_pixel()

        self.ref_x, self.ref_y = ref[:]
        self.ref_s = self.get_reference_spectrum()

        # Calculate the FWHM ---------------------------------------------------
        self.fwhm = self.get_fwhm()

        # Calculate the finesse ------------------------------------------------
        self.finesse = self.get_finesse()

        # Get the correlation cube ---------------------------------------------
        if correlation:
            self.extract_from = self.use_correlation()
        else:
            self.extract_from = self.input_file

        if self.verbose:
            log.info(" Ideal number of channels: %.1f channels"
                     % round(2 * self.finesse))
            log.info(" Ideal sampling: %.1f %s / channel"
                     % (self.free_spectral_range / round(2 * self.finesse),
                        self.units))

        self.phase_map = self.extract_phase_map()
        self.save()

        return

    def extract_phase_map(self):
        """
        Extract the phase-map using numpy.argmax.

        Returns
        -------
            phase_map : numpy.ndarray
                A 2D array that contains the phase-map, i. e., the channel
                in *bcv* with maximum intensity for each pixel.

        See also
        --------
            numpy.argmax
        """

        now = time.time()

        try:
            sampling = self.header['C3_3']
        except KeyError:
            sampling = 1

        # Reading data
        if self.verbose:
            log.info("\n Starting phase-map extraction.")
            log.info(" Reading data from %s file" % self.extract_from)
        data = pyfits.getdata(self.extract_from)

        # Extracting phase-map
        if self.verbose:
            log.info(" Extracting phase-map...")
        data = np.where(data > data.mean() + data.std(), data, -np.inf)
        phase_map = np.argmax(data, axis=0) * sampling

        if self.verbose:
            log.info(" Done in %.2f seconds" % (time.time() - now))
        return phase_map

    def find_reference_pixel(self):
        """
        Read the reference pixel from header or find it.

        Returns
        -------
            ref_x : int
                X position of the center of the rings.

            ref_y : int
                Y position of the center of the rings.
        """
        if self.verbose:
            log.info("\n Finding reference pixel.")

        if ('PHMREFX' in self.header) and ('PHMREFY' in self.header):

            if self.verbose:
                log.info(" Found reference pixel found in header.")

            ref_x = self.header['PHMREFX']
            ref_y = self.header['PHMREFY']

            if self.verbose:
                log.info(" Using [%d, %d]" % (ref_x, ref_y))

        else:
            if self.verbose:
                log.info(" Reference pixel NOT found in header.")
                log.info(" Trying to find the center of the rings.")
                ref_x, ref_y = self.find_rings_center(self.fsr_channel)

            # try:
            #     ref_x, ref_y = self.find_rings_center()
            # except ValueError:
            #     log.warn('Could not find the center of the rings. Using '
            #              'center of image')
            #     ref_x = self.header['NAXIS1'] // 2
            #     ref_y = self.header['NAXIS2'] // 2

        return ref_x, ref_y

    def find_rings_center(self, fsr, n_interactions=20):
        """
        Method used to find the center of the rings inside a FP data-cube by
        cutting it in two directions (XZ to find Y center and YZ to find X
        center), fitting a 2nd degree polynomium and get its extrema points.

        Parameters
        ----------
            fsr : float
                The free-spectral-range in number of channels

            n_interactions : int
                Number of interactions to find the center.

        Returns
        -------
            ref_x : int
                X position of the center of the rings.

            ref_y : int
                Y position of the center of the rings.
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
        log.info(" Start center finding.")
        old_ref_x = ref_x
        old_ref_y = ref_y

        if self.show:
            plt.figure()

        # Starting interactions
        for i in range(n_interactions):

            ref_y = max(ref_y, 0)
            ref_y = min(ref_y, height -  1)

            ref_x = max(ref_x, 0)
            ref_x = min(ref_x, width - 1)

            # Get a slice from cube ---
            temp_x = self.data[:, ref_y, x]
            temp_y = self.data[:, y, ref_x]

            # Create a pool to find the Z position in each row/column
            p = Pool(16)
            px = PeakFinder(temp_x)
            py = PeakFinder(temp_y)

            temp_x = np.array(p.map(px, range(x.size)))
            temp_y = np.array(p.map(py, range(y.size)))

            # Reshape into two dimensions so the clustering works
            X = np.array(zip(temp_x, np.zeros(len(temp_x))), dtype=np.int)
            Y = np.array(zip(temp_y, np.zeros(len(temp_y))), dtype=np.int)

            # Use MeanShift algorithm to cluster the data
            ms = MeanShift(bandwidth=fsr//2)
            ms.fit(X)

            labels_unique = np.unique(ms.labels_)
            n_clusters = len(labels_unique)
            if n_clusters == 2:
                cluster_centers =  ms.cluster_centers_[ms.labels_, 0]
                temp_x = \
                    np.where(cluster_centers < fsr // 2, temp_x, temp_x - fsr)
            elif n_clusters > 2:
                log.warning("Your data-cube may contain more than 2 FSR. \n"
                            "I don't know how to deal with that")

            # Same for Y
            ms = MeanShift(bandwidth=fsr // 2)
            ms.fit(Y)

            labels_unique = np.unique(ms.labels_)
            n_clusters = len(labels_unique)
            if n_clusters > 1:
                cluster_centers = ms.cluster_centers_[ms.labels_, 0]
                temp_y = \
                    np.where(cluster_centers < fsr // 2, temp_y,
                                  temp_y - fsr)

            # Not that it is fixed, I can fit the parabola
            px = scipy.polyfit(x, temp_x, 2)
            py = scipy.polyfit(y, temp_y, 2)

            ref_x = int(round(- px[1] / (2.0 * px[0])))
            ref_y = int(round(- py[1] / (2.0 * py[0])))

            # Selecting valid data
            error_x = np.abs(temp_x - scipy.polyval(px, x))
            error_y = np.abs(temp_y - scipy.polyval(py, y))

            if self.show:
                plt.title("Finding center of the rings")
                plt.clf()
                fig = plt.gcf()
                gs = gridspec.GridSpec(2, 1, height_ratios=[6, 2])

                ax1 = plt.subplot(gs[0])
                ax1.plot(x, temp_x, 'b.', alpha=0.25)
                ax1.plot(x, scipy.polyval(px, x), 'b-', lw=2)
                ax1.plot(y, temp_y, 'r.', alpha=0.25)
                ax1.plot(y, scipy.polyval(py, y), 'r-', lw=2)
                #ax1.yaxis.set_ticklabels([])
                ax1.axvline(ref_x, ls='--', c='blue', label='x')
                ax1.axvline(ref_y, ls='--', c='red', label='y')
                ax1.legend(loc='best')
                ax1.grid()
                ax1.set_ylabel("Iteration number %d" % (i + 1))

                ax2 = plt.subplot(gs[1], sharex=ax1)
                ax2.plot(x, temp_x - scipy.polyval(px, x), 'o', color='b', alpha=0.25)
                ax2.plot(y, temp_y - scipy.polyval(py, y), 'o', color='r', alpha=0.25)
                fig.add_axes(ax2)

            # Measuring the error
            xl = np.diff(temp_x)
            yl = np.diff(temp_y)
            cond_x = np.where(error_x <= 3 * np.abs(np.median(xl[xl != 0])), True, False)
            cond_y = np.where(error_y <= 3 * np.abs(np.median(yl[yl != 0])), True, False)

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

                if self.verbose:
                    log.info(" Rings center found at: [%d, %d]" % (ref_x, ref_y))
                    log.info(" Done in %.2f s" % (time.time() - now))

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
            reply = raw_input('? ')
            if reply.lower() == 'n':
                log.warning('Ok then. Moving forward.')
                sys.exit()
            if reply.lower() == 'y':
                log.warning('Ok then. Moving forward.')
                return ref_x, ref_y

        log.warning("Do you want to continue? [Y,n]")
        reply = '.'
        while reply not in ' yn':
            reply = raw_input('? ')
            if reply.lower() == 'n':
                log.warning('Ok then. Leaving now.')
                sys.exit()

        log.info("    Then, enter the reference X in pixel:")
        log.info("    Leave it empty to get it in the center of the image")
        reply = '.'
        while not reply.isdigit():
            reply = raw_input('? ')
            if reply == '':
                reply = self.header['NAXIS1'] // 2
                break
        ref_x = int(reply)

        log.info("    Then, enter the reference Y in pixels:")
        log.info("    Leave it empty to get it in the center of the image")
        reply = '.'
        while not reply.isdigit():
            reply = raw_input('? ')
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

        if self.verbose:
            log.info(" Done in %.2f s" % (time.time() - now))
            log.info(" Using [%d, %d]." % (ref_x, ref_y))

        return ref_x, ref_y

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
            log.info(" Finesse = %.1f" % finesse)

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

        if self.verbose:
            log.info(" Finding the free-spectral-range.")

        now = time.time()

        # First frame is the reference frame
        ref_frame = self.data[0, :, :]

        # Subtract all frames from the first frame
        data = self.data - ref_frame

        # Get the absolute value
        data = np.abs(data)

        # Sum over the spatial directions
        data = data.sum(axis=2)
        data = data.sum(axis=1)

        # Interpolate data
        s = interpolate.interp1d(self.z, data, kind='cubic')
        z = np.linspace(self.z[4], self.z[-1], 10000)

        # Find the free-spectral-range in z units
        fsr = z[np.argmin(s(z))] - self.z[0]
        fsr = np.abs(fsr)
        log.info('FSR = %.2f' % fsr)

        # Find the free-spectral-range in number of channels
        fsr_index = np.argmin(np.abs(self.z - z[np.argmin(s(z))]))

        # Fix for Python index style
        fsr_channel = fsr_index + 1
        log.info('FSR channel = %d' % fsr_channel)

        # What if my cube has less than a FSR or could not find it?
        if fsr_channel == 4:

            log.info("[!] FSR could not be found.")
            log.info("    Do you want to continue? [Y,n]")

            reply = '.'
            while reply not in ' yn':
                reply = raw_input('? ')
                if reply.lower() == 'n':
                    sys.exit()

            log.info("    Then, enter a FSR in Z units (usually BCV):")
            reply = '.'
            while not reply.isdigit():
                reply = raw_input('? ')
            fsr = float(reply)

            log.info("    Then, enter a FSR in number of channels:")
            reply = '.'
            while not reply.isdigit():
                reply = raw_input('? ')
            fsr_channel = int(reply)

        elif fsr_channel == len(data):
            log.info(" It seems that you scanned exactly over a FSR.")
            log.info(" If not, check your data and phasemap_fit again.")

        # Calculate the sampling
        sampling = fsr / fsr_index

        if self.verbose:
            log.info(" FSR = %.1f %s" % (fsr, self.units))
            log.info("     = %d channels" % fsr_channel)
            log.info(" Sampling = %.1f %s / channel" % (sampling, self.units))
            log.info(" Done in %.2f s" % (time.time() - now))

        # Plot to see how it goes
        if self.show:
            plt.title("Finding the Free-Spectral-Range")
            plt.plot(self.z, data, 'ko', label='Measured data')
            plt.plot(z, s(z), 'k-', lw=2, label='3rd deg spline fitting')
            plt.xlabel("z [%s]" % self.units)
            plt.axvline(x=(self.z[fsr_index]), ls='--', c='gray',
                        label='Free-Spectral-Range \nat z = %.1f' % fsr)
            plt.legend(loc='best')
            plt.xlim(self.z[0], self.z[-1])
            plt.gca().yaxis.set_ticklabels([])
            plt.grid()
            plt.tight_layout()
            plt.show()

        return fsr, fsr_channel

    def save(self):
        """
        Save files.
        """
        from os.path import splitext

        v = self.verbose
        f = splitext(self.input_file)[0]
        h = self.header.copy()
        h['PHMREFX'] = self.ref_x
        h['PHMREFY'] = self.ref_y
        h.set('', '', before='PHMREFX')
        h.set('', '--- PHM Xtractor ---', before='PHMREFX')

        fsr = self.free_spectral_range

        h['PHMREFF'] = (self.input_file, 'Original file')
        h['PHMTYPE'] = 'observed'
        h['PHMUNIT'] = self.units
        h['PHMFSR'] = (round(fsr, 2),
                       'Free-spectral-range in %s units' % self.units)
        try:
            h['PHMSAMP'] = (self.header['C3_3'], 'Used sample [%s / channel].'
                            % self.units)
        except KeyError:
            h['PHMSAMP'] = 1

        self.phase_map = self.phase_map - self.phase_map[self.ref_y, self.ref_x]

        try:
            del (h['CRPIX3'], h['CRVAL3'], h['C3_3'], h['CDELT3'])
        except KeyError:
            pass

        filename = safe_save(f + "--obs_phmap.fits", overwrite=True, verbose=v)
        log.info(" Saving observed phase-map to file: %s" % filename)
        pyfits.writeto(filename, self.phase_map, h, clobber=True)

        filename = safe_save(f + "--ref_spec.fits", overwrite=True, verbose=v)
        log.info(" Saving reference spectrum to file: %s" % filename)
        pyfits.writeto(filename, self.ref_s, h, clobber=True)

        return

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



if __name__ == '__main__':
    log_fmt = MyLogFormatter()
    log_handler = logging.StreamHandler()
    log_handler.setLevel(logging.DEBUG)

    log_handler.setFormatter(log_fmt)
    log.addHandler(log_handler)

    main()
