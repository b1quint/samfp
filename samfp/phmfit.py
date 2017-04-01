#!/usr/bin/python
# -*- codign: utf8 -*-
"""
    2014.04.16 15:51 - Fixed keyword to access phase-map sampling.
    2014.08.25 18:30 - Fixed ref_x/ref_y
                     - Show phmap, ref_x/ref_y, npoints
"""
from __future__ import division, print_function

import argparse
import astropy.io.fits as pyfits
import logging
import matplotlib.pyplot as plt
import numpy as np
import os


class PhaseMapFit:
    def __init__(self, log=None):
        self.log = self.get_logger() if log is None else log

    def get_concavity_sign(self, dz, sampling):

        self.log.info("Checking concavity sign:")
        dz_abs = np.abs(dz)
        dz_sign = np.sign(dz)
        sign = np.median(dz_sign[(dz_sign != 0) * (dz_abs <= np.abs(sampling))])

        self.log.info("Parabola is %s" % ('up' if sign > 0 else 'down'))
        return sign

    def get_map_dimensions(self, header):
        """
        Returns the number of rows (map height) and the number of columns (map
        width) in number of pixels.

        :param header: the phasemap header.
        :type header: pyfits.Header

        :return n_cols: map width (number of columns).
        :rtype n_cols: int

        :return n_rows: map height (number of rows).
        :rtype n_rows: int
        """
        h = header
        log = self.log

        n_cols = h['NAXIS1']
        n_rows = h['NAXIS2']
        log.info('Input phase-map dimensions are: [%d, %d]' % (n_rows, n_cols))

        return n_cols, n_rows

    def get_logger(self):
        """Create and return a customized logger object.

        :return log: the logger object.
        :rtype log: logging.Logger
        """
        lf = MyLogFormatter()

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(lf)

        logging.captureWarnings(True)
        log = logging.getLogger("phasemap_fit")
        log.setLevel(logging.INFO)
        log.addHandler(ch)

        return log

    def get_reference_pixel(self, header):
        """
        Look for the reference pixel in the phasemap header. This is necessary
        to know the center of the rings and to do the radial plot. If it is
        not found, it returns the coordinated at the center of the image.

        :param header: the phasemap header.
        :type header: pyfits.Header

        :return ref_x: reference X coordinate.
        :rtype ref_x: int

        :return ref_y: reference Y coordinate.
        :rtype ref_y: int
        """

        log = self.log
        h = header

        ref_x = h['PHMREFX']
        ref_y = h['PHMREFY']
        try:
            ref_x = h['CRPIX1'] + (ref_x - h['CRVAL1']) / h['CDELT1']
            ref_y = h['CRPIX2'] + (ref_y - h['CRVAL2']) / h['CDELT2']
        except KeyError:
            log.warn("WCS not found. Using phisical coordinates.")

        log.info('Reference pixel: [%d, %d]' % (ref_x, ref_y))

        return ref_x, ref_y

    def print_header(self):
        """Just print a nice header to show when the script is running."""
        log = self.log
        log.info("\n Phase-Map Fitting for BTFI")
        log.info("by Bruno Quint & Fabricio Ferrari")
        log.info("version 0.0a - Jan 2014\n")

    def read_observed_phasemap(self, filename):
        """
        Read the observed phase-map and return it and its header.

        :param filename: the observed phase-map filename.
        :type filename: str

        :return data: the observed phase-map.
        :rtype data: np.ndarray

        :return header: the observed phase-map's header.
        :rtype header: pyfits.Header
        """
        log = self.log
        log.info('Reading data from "%s"' % filename)

        data = pyfits.getdata(filename)
        header = pyfits.getheader(filename)

        log.info('Done.')
        return data, header

    def run(self, filename, n_points=10, interactions=5, show=False):

        log = self.log

        self.print_header()
        d, h = self.read_observed_phasemap(filename)

        log.info("\n Starting phase-map fitting.")
        log.info("[%d x %d] will be used to sample the observed phase-map"
                 % (n_points, n_points))
        log.info("%d interactions will be used for fitting" % interactions)

        log.info("Graphics/plots will%s be displayed.\n" %
                 ('' if show else ' not'))

        ref_x, ref_y = self.get_reference_pixel(h)
        n_cols, n_rows = self.get_map_dimensions(h)

        # Subtract reference value from the phase-map so the map becomes
        # relative
        # d -= d[ref_y, ref_x]

        # Get sample points
        x = (np.linspace(0.05, 0.95, n_points) * n_cols).astype(int)
        y = (np.linspace(0.05, 0.95, n_points) * n_rows).astype(int)
        X, Y = np.meshgrid(x, y)

        # Select subsample
        Z = d[Y, X]

        # Convert [X,Y] to radial coordinates
        R = np.sqrt((X - ref_x) ** 2 + (Y - ref_y) ** 2)

        unit = h['PHMUNIT']
        sampling = h['PHMSAMP']
        FSR = float(h['PHMFSR'])

        self.show_sampled_phasemap(d, ref_x, ref_y, n_cols, n_rows, X, Y, unit, show)

        # Flatten sampled data
        x, y, z = np.ravel(X), np.ravel(Y), np.ravel(Z)

        # Radial plot
        r = np.sqrt((x - ref_x) ** 2 + (y - ref_y) ** 2)

        # I have no idea of what I am doing here
        condition = np.where(z > z.min(), True, False) * \
                    np.where(z < z.max(), True, False)

        r = r[condition]
        z = z[condition]

        z = z[np.argsort(r)]
        r = np.sort(r)
        dz = np.diff(z, 1)

        sign = self.get_concavity_sign(dz, sampling)

        # Tell me the limits to fit the first parabola
        dz_abs = np.abs(dz)
        dz_abs_crit = dz_abs >= FSR / 2
        print(np.any(dz_abs_crit))
        if np.any(dz_abs_crit):
            where = np.argmin(np.abs(r[dz_abs_crit][0] - r))
        else:
            where = (r.size - 1)

        # Plot the gradient
        if args.show_plots:
            plt.figure(figsize=(16, 7))
            plt.subplot(2, 2, 3)
            plt.plot(r[1:], dz, 'b-')
            plt.gca().yaxis.set_label_position("right")
            plt.axvline(r[where], color='black', lw=2, ls='--')
            plt.axhline(FSR / 2, color='red', ls='--', label="FSR")
            plt.axhline(- FSR / 2, color='red', ls='--')
            plt.xlabel('Radius [px]')
            plt.ylabel('Gradient \n [%s]' % unit)
            plt.legend(loc='best')
            plt.grid()

        if args.show_plots:
            plt.subplot(2, 2, 1)
            plt.plot(r[:where], z[:where], 'b.', alpha=0.25, label='Not to be fixed')
            plt.plot(r[where:], z[where:], 'r.', alpha=0.25, label='Data to be fixed')
            plt.axvline(r[where], color='black', lw=2, ls='--')
            plt.gca().yaxis.set_label_position("right")

            plt.xlabel('Radius [px]')
            plt.ylabel('Peak displacement \n [%s]' % unit)

            plt.legend(loc='best')
            plt.grid()

        # Plot data after correction
        delta = 10
        z = (z + sign * delta + sign * FSR) % FSR + sign * FSR - sign * delta
        if args.show_plots:
            ax_fit = plt.subplot(2, 2, 2)
            ax_fit.plot(r, z, 'r.',
                        alpha=0.25, label='Fixed data')
            ax_fit.yaxis.set_label_position("right")
            ax_fit.set_xlabel('Radius [px]')
            ax_fit.set_ylabel('Peak displacement \n [%s]' % unit)
            ax_fit.grid()

            ax_err = plt.subplot(224)
            ax_err.yaxis.set_label_position("right")
            ax_err.set_xlabel('Radius [px]')
            ax_err.set_ylabel('Peak displacement \n [%s]' % unit)
            ax_err.grid()

        # Fit data
        for i in range(interactions):

            p = np.polyfit(r, z, deg=2)
            rr = np.linspace(r[0], r[-1], 10000)
            zz = np.polyval(p, rr)
            err = (z - np.polyval(p, r))
            if show:
                ax_fit.plot(rr, zz, 'k-', alpha=0.25)
                ax_err.plot(r, err, 'k-', alpha=0.25)

            log.info('%02d interaction' % i)
            log.info("Average err = %.2f" % err.mean())
            log.info("Error STD = %.2f" % err.std())

            c = np.where(np.abs(err) <= 2 * np.abs(sampling))
            r = r[c]
            z = z[c]

        log.info("  phi(x,y) = %.2e x^2 + %.2e x + %.2e " % (p[0], p[1], p[2]))
        log.info("  Error abs min: %f" % np.abs(err).min())
        log.info("  Error avg: %f" % err.mean())
        log.info("  Error std: %f" % err.std())
        log.info("  Error rms: %f" % np.sqrt(((err ** 2).mean())))
        log.info("  Sampling in Z: %s" % h['phmsamp'])
        log.info(" ")

        x = np.arange(n_cols)
        y = np.arange(n_rows)
        X, Y = np.meshgrid(x, y)
        R = np.sqrt((X - ref_x) ** 2 + (Y - ref_y) ** 2)
        Z = np.polyval(p, R)
        Z = Z - Z[ref_y, ref_x]

        h['PHMTYPE'] = 'parabola fit'
        fname = h['PHMREFF']
        fname = os.path.splitext(fname)[0]
        pyfits.writeto(fname + '--fit_phmap.fits', Z, h, clobber=True)
        pyfits.writeto(fname + '--res_phmap.fits', Z - d, h, clobber=True)

        log.info(" All done.\n")

        if args.show_plots:
            plt.show()

    def set_log_level(self, level):
        """
        Set the internal logger level.

        :param level: logger level.
        :type level: logger.DEBUG|logger.WARNING|logger.CRITICAL
        """
        self.log.setLevel(level)

    def show_sampled_phasemap(self, data, x0, y0, w, h, X, Y, unit, show):

        if not show: return

        self.log.info('A new window has opened. '
                      'Check it and close it to continue.')

        fig = plt.figure()
        ax = fig.add_subplot(111)

        ax.scatter(x0, y0, c='orange', s=400, marker="+", lw=3)
        ax.scatter(X, Y, c='g', s=1, marker=".", alpha=0.7)
        ax.set_xlabel("X [px]")
        ax.set_ylabel("Y [px]")
        ax.set_xlim(0, w)
        ax.set_ylim(0, h)
        ax.grid()

        img = ax.imshow(data, origin='lower', interpolation='nearest',
                        cmap='coolwarm')
        cbar = plt.colorbar(img)
        cbar.set_label('Z [%s]' % unit)

        plt.show()


def get_colormap():
    from matplotlib import colors

    cdict = {'red': ((0.0, 1.0, 1.0),
                     (0.25, 1.0, 1.0),
                     (0.5, 0.0, 0.0),
                     (0.75, 0.0, 0.0),
                     (1.0, 0.9, 0.9)),
             'green': ((0.0, 0.9, 0.9),
                       (0.25, 0.0, 0.0),
                       (0.5, 0.0, 0.0),
                       (0.75, 0.0, 0.0),
                       (1.0, 0.9, 0.9)),
             'blue': ((0.0, 0.9, 0.9),
                      (0.25, 0.0, 0.0),
                      (0.5, 0.0, 0.0),
                      (0.75, 1.0, 1.0),
                      (1.0, 1.0, 1.0))}

    return colors.LinearSegmentedColormap('heaven_hell', cdict, 256)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    DIM = '\e[2m'
    ENDDIM = '\e[22m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''


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


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Fits an existing phase-map.")

    parser.add_argument('filename', type=str,
                        help="Input phase-map name.")
    parser.add_argument('-d', '--debug', action='store_true',
                        help="Run program quietly.")
    parser.add_argument('-i', '--interactions', default=5, type=int,
                        help="Number of interactions in the process [5]")
    parser.add_argument('-n', '--npoints', default=50, type=int,
                        help="Number of points that will be used to fit the phase-map [50]")
    parser.add_argument('-o', '--output', type=str, default=None,
                        help="Name of the output phase-map file.")
    parser.add_argument('-q', '--quiet', action='store_true',
                        help="Run program quietly.")
    parser.add_argument('-s', '--show_plots', action='store_true',
                        help="Show plots.")

    args = parser.parse_args()

    phmfit = PhaseMapFit()

    if args.quiet:
        phmfit.set_log_level(level=logging.ERROR)

    if args.debug:
        phmfit.set_log_level(level=logging.DEBUG)

    phmfit.log.debug("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    phmfit.run(args.filename,
               interactions=args.interactions, n_points=args.npoints,
               show=args.show_plots)