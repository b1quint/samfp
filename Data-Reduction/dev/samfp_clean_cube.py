#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
    Script that cleans a data-cube that is already fully reduced. That means
    that the cube is already mounted, the phase-correction was already applied,
    WCS is already in the header and the wavelength calibration is also applied.
"""
from __future__ import division, print_function

import argparse
import astropy.io.fits as pyfits
import logging
import numpy as np
import matplotlib.pyplot as plt

from scipy import fftpack
from scipy import ndimage

__author__ = 'Bruno Quint'


class MyLogFormatter(logging.Formatter):

    err_fmt  = "ERROR: %(msg)s"
    dbg_fmt  = " DBG: %(module)s: %(lineno)d: %(msg)s"
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
        description="Clean FP data-cube.")

    parser.add_argument('data_cube', type=str,
        help="Cube to be cleaned.")
    parser.add_argument('-d', '--debug', action='store_true',
        help="Run program in debug mode.")
    parser.add_argument('-q', '--quiet', action='store_true',
        help="Run program quietly.")
    parser.add_argument('-s', '--show_plots', action='store_true',
        help="Show plots.")

    args = parser.parse_args()

    log_formatter = MyLogFormatter()
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(log_formatter)
    log = logging.getLogger()
    log.addHandler(log_handler)

    # Load Data ---
    log.info('Loading %s file' % args.data_cube)
    data = pyfits.getdata(args.data_cube)
    header = pyfits.getheader(args.data_cube)

    # Spatial Clean --
    data = np.sum(data, axis=0)
    fft_image = fftpack.fft2(data)
    fft_image = fftpack.fftshift(fft_image)

    fft_image = fftpack.ifftshift(fft_image)
    data = fftpack.ifft2(fft_image)
    data = data.real

    plt.figure()
    vmin = fft_image.real.mean() - fft_image.real.std()
    vmax = fft_image.real.mean() + fft_image.real.std()
    plt.subplot(211)
    plt.imshow(fft_image.real, origin='lower', cmap='gray_r', interpolation='nearest', vmin=vmin, vmax=vmax)
    plt.show()

    vmin = data.mean() - data.std()
    vmax = data.mean() + data.std()
    plt.subplot(222)
    plt.imshow(data, origin='lower', cmap='gray_r', interpolation='nearest', vmin=vmin, vmax=vmax)
    plt.show()


