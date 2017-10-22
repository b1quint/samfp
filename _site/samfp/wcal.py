#!/usr/bin/env python 
# -*- coding: utf8 -*-
from __future__ import division, print_function

import argparse
import threading
import sys

from astropy.io import fits as pyfits
from scipy import signal

import numpy as np

from .tools import io, version

log = io.MyLogger(__name__)


__author__ = 'Bruno Quint'


class WavelengthCalibration(threading.Thread):

    key_zfsr = 'PHM_FSR'
    key_z_step = 'CDELT3'

    def __init__(self, input_file, gap_size, debug_mode=False, output=None,
                 verbose_mode=False, wavelength=None):

        threading.Thread.__init__(self)
        global log

        self.gap_size = gap_size
        self.log = log
        self.input_file = input_file
        self.output_file = output
        self.wavelength = wavelength

        self.log.set_verbose(verbose=verbose_mode)
        self.log.set_debug(debug=debug_mode)

        self.info = self.log.info
        self.debug = self.log.debug
        self.error = self.log.error
        self.warn = self.log.debug

        return

    def run(self):

        self.info()

        self.info("")
        self.info("SAM-FP Tools: Wavelength Calibration")
        self.info("by Bruno Quint (bquint@ctio.noao.edu)")
        self.info("version {:s}".format(version.__str__))
        self.info("Starting program.")
        self.info("")

        self.info("Input filename: {0.input_file:s}".format(self))
        self.info("Output filename: {0.output_file:s}".format(self))

        # Seistemic wavelength
        try:
            header = pyfits.getheader(self.input_file)
        except IOError:

            self.error("\n File not found:\n {0.input_file:s}".format(self))
            self.error(" Leaving program now.")
            sys.exit(1)

        if self.wavelength is None:
            try:
                self.wavelength = header['PHMWCAL']
                self.info("\n Seistemic wavelength found in the header: "
                          "\n CRVAL = {0.wavelength:.2f} Angstrom".format(self))
            except KeyError:
                msg = ("\n No wavelength could be found. "
                       "Leaving program now.")
                self.error(msg)
                sys.exit(1)
        else:
            self.info("\n Seistemic wavelength providen by the user: "
                      "\n CRVAL = {0.wavelength:.2f} Angstrom".format(self))

        header.set('CRVAL3', value=self.wavelength,
                   comment='Seistemic wavelength.')

        # Finding the reference pixel
        data = pyfits.getdata(self.input_file)
        s = np.mean(data, axis=2)
        s = np.mean(s, axis=1)

        midpt = np.median(s)
        std = np.std(s)

        self.debug(" Collapsed data statistics: ")
        self.debug(" median = {:.2f}".format(midpt))
        self.debug(" std = {:.2f}".format(std))

        p = np.percentile(data, 50.)
        s_ = s.copy()
        s_[s < p] = 0.

        k = signal.general_gaussian(10, 1, 5)
        cc = signal.correlate(s_[5:-5], k, mode="same")
        self.arg_max = np.argmax(cc) + 5

        self.info("Reference channel is: ")
        self.info("CRPIX3 = {0.arg_max:d}")
        header.set('CRPIX3', value=self.arg_max)

        # Find the step in angstroms
        try:
            z_fsr = header[self.key_zfsr]
        except KeyError:
            self.warn('%s card was not found in the header.' % self.key_zfsr)
            z_fsr = input('    Please, enter the Free-Spectral-Range in bcv:'
                          '\n    > ')
        except TypeError:
            z_fsr = input('    Please, enter the Free-Spectral-Range in bcv:'
                          '\n    >  ')

        try:
            z_step = header[self.key_z_step]
        except KeyError:
            self.warn('%s card was not found in the header.' % self.key_z_step)
            z_step = input('    Please, enter the step between channels in bcv'
                           '\n     >  ')
        except TypeError:
            self.warn('Header was not passed to "WCal.get_wavelength_step"'
                      ' method')
            z_step = input('    Please, enter the step between channels in bcv'
                           '\n    >  ')

        gap_size = self.gap_size * 1e-6
        self.info(' Gap size e = {:.1f} um'.format(gap_size * 1e6))

        self.wavelength = self.wavelength * 1e-10
        w_order = 2 * gap_size / self.wavelength
        self.info(' Interference order p({:.02f}) = {:.2f}'.format(
            self.wavelength * 1e10, w_order))

        self.info(' Z Free-Spectral-Range = {:.02f} bcv'.format(z_fsr))
        w_fsr = self.wavelength / (w_order * (1 + 1 / w_order ** 2))
        self.info(' W Free-Spectral-Range = {:.02f} A'.format(w_fsr * 1e10))

        w_step = w_fsr / z_fsr * z_step
        QGC = w_fsr / z_fsr * 1e10
        self.info(' Queesgate constant = {:.02f} A / bcv'.format(QGC))
        self.info(' Step = {:.02f} A / channel'.format(w_step * 1e10))

        w_step *= 1e10
        header.set('CDELT3', value=w_step)
        header.set('C3_3', value=w_step)


        header.set('WCAL_W0', value=self.wavelength,
                   comment='Seistemic Wavelength [A]', after='PHMFIT_C')
        header.set('WCAL_DW', value=self.wavelength,
                   comment='Wavelength increment / channel [A]',
                   after='PHMFIT_C')
        header.add_blank('-- sam-fp wavelength calibration --',
                         after='PHMFIT_C')

        pyfits.writeto(self.input_file.replace('.fits', '_wcal.fits'), data,
                       header, overwrite=True)


def parse_arguments():

    parser = argparse.ArgumentParser(description="Find the wavelength "
                                                 "calibration for a data-cube "
                                                 "observed with the SAM-FP")

    parser.add_argument('filename', type=str, help="Input data-cube.")
    parser.add_argument('gap_size', type=float,
                        help="Fabry-Perot nominal gap size [um]")
    parser.add_argument('-d', '--debug', action='store_true',
                        help="Run program in debug mode.")
    parser.add_argument('-o', '--output', type=str, default=None,
                        help="Name of the output phase-map file.")
    parser.add_argument('-q', '--quiet', action='store_true',
                        help="Run program quietly.")

    _args = parser.parse_args()
    return _args


if __name__ == '__main__':

    args = parse_arguments()

    wavelength_calibration = WavelengthCalibration(
        args.filename,
        args.gap_size,
        debug_mode=args.debug,
        output=args.output,
        verbose_mode=not args.quiet
    )

    wavelength_calibration.start()
    wavelength_calibration.join()

    if wavelength_calibration.is_alive():
        wavelength_calibration.log.warn(" A thread is still running.")
    else:
        wavelength_calibration.log.info(" All done.")