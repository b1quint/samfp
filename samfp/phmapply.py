#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
     Phase-Map Apply - A script to apply a phase-map on a data-cube.
     by Bruno Quint (bquint@astro.iag.usp.br)
     and Fabricio Ferrari (fabricio@ferrari.pro.br)
     version 0.0 - Feb 2014
"""

from __future__ import division, print_function

import argparse
import os
import sys
import time

import astropy.io.fits as pyfits
import numpy as np
from scipy.interpolate import UnivariateSpline
from scipy import signal

from . import io
from .tools import version

_log = io.get_logger(__name__)


def main():

    parser = argparse.ArgumentParser(
        description="Apply a phase-map on a data-cube."
    )
    parser.add_argument(
        '-c', '--center', action='store_true',
        help="Try to center the strongest line in the cube."
    )
    parser.add_argument(
        '-n', '--npoints', type=int, default=10,
        help="Number of points in the re-sampling for channel [10]."
    )
    parser.add_argument(
        '-o', '--output', metavar='output', type=str, default=None,
        help="Name of the output corrected cube"
    )
    parser.add_argument(
        '-q', '--quiet', action='store_true',
        help="Run it quietly."
    )
    parser.add_argument(
        '-v', '--velocity', type=float, default=0.0,
        help="Systemic velocity to be applied to the emitted wavelength [km/s]."
    )
    parser.add_argument(
        'cube_file', metavar='cube_file', type=str,
        help="Input calibration cube filename."
    )
    parser.add_argument(
        'map_file', metavar='map_file', type=str,
        help="Input phase-map image filename."
    )
    parser.add_argument(
        'wavelength', type=float,
        help="Average systemic wavelength or emitted wavelength."
    )
    parser.add_argument(
        'gap_size', type=float,
        help="Nominal gap size [um]."
    )

    args = parser.parse_args()
    if args.quiet:
        _log.setLevel('ERROR')
    else:
        _log.setLevel('INFO')

    # Printing program header --------------------------------------------------
    start = time.time()
    _log.info("")
    _log.info("SAM-FP Tools: PHase-Map Apply")
    _log.info("by Bruno Quint (bquint@ctio.noao.edu)")
    _log.info("version {:s}".format(version.__str__))
    _log.info("Starting program.")
    _log.info("")

    root_dir = os.path.dirname(args.cube_file)
    cube_file = args.cube_file
    map_file = args.map_file

    if args.output is None:
        out_file = 'phc_' + os.path.split(args.cube_file)[-1]
    else:
        out_file = args.output

    _log.info("Root dir: %s" % root_dir)
    _log.info("Cube to be corrected: %s" % cube_file)
    _log.info("Phase-map to be applied: %s" % map_file)
    _log.info("Output corrected cube: %s" % out_file)

    # Systemic wavelength ------------------------------------------------------
    vel = args.velocity
    c = 299792 # km/s
    wavelength = args.wavelength * np.sqrt((1 + vel / c) / (1 - vel / c))

    _log.info("")
    _log.info("Emitted/systemic wavelength: %.2f A" % args.wavelength)
    _log.info("Systemic velocity: %.2f km/s" % vel)
    _log.info("Observed wavelength: %.2f A" % wavelength)

    # Reading input data ------------------------------------------------------
    _log.info("")
    _log.info("Reading cube to be corrected.")
    data_cube = pyfits.open(cube_file)[0]
    _log.info("Done.")

    _log.info("Reading phase-map to be applied.")
    phase_map = pyfits.open(map_file)[0]
    _log.info("Done.")

    # Checking data -----------------------------------------------------------
    if data_cube.data[0].shape != phase_map.shape:
        _log.error("Cube and map does not have matching width and height.")
        _log.error("[!] Leaving now.\n")
        sys.exit()

    if data_cube.data.ndim != 3:
        _log.error("[!] Cube file is not really a cube.")
        _log.error("[!] Leaving now.\n")
        sys.exit()

    if phase_map.data.ndim != 2:
        _log.error("[!] Map file is not really an image.")
        _log.error("[!] Leaving now.\n")
        sys.exit()

    m = data_cube.header['NAXIS1']
    n = data_cube.header['NAXIS2']

    ref_x = phase_map.header['PHMREFX']
    ref_y = phase_map.header['PHMREFY']
    units = phase_map.header['PHMUNIT']

    # TODO -- fix this
    try:
        sample = float(data_cube.header['CDELT3'])
    except KeyError:
        _log.error('"CDELT3" keyword was not found in the header.')
        sample = 1

    # Reading the Free-Spectral-Range --------------------------------------
    try:
        _log.info("")
        _log.info("Reading free-spectral-range from cube header.")
        # TODO add an option to use the FSR found while extracting
        # TODO the phase-map or while fitting it.
        # TODO or even to give the option for the user to enter it.
        cal_fsr = phase_map.header['PHM_FSR']
        cal_wavelength = phase_map.header['PHMWCAL']
        f_s_r = cal_fsr / cal_wavelength * wavelength
        _log.info(" Free Spectral Range = %.2f %s" % (f_s_r, units))

    except KeyError:
        _log.info("Please, enter the free-spectral-range in %s units" % units)
        f_s_r = io.input("    >")

    f_s_r = round(f_s_r / abs(sample)) # From BCV to Channels
    _log.info("Free-Spectral-Range is %d channels" % f_s_r)

    fsr = f_s_r * args.npoints  # From Channels to nPoints
    fsr = int(round(fsr))
    _log.info("Free-Spectral-Range is %d points" % fsr)

    # Assure that the reference spectrum will not be moved ----------------
    try:
        phase_map.data = phase_map.data - phase_map.data[ref_y, ref_x]
    except IndexError:
        _log.warning("Reference pixel out of field.")
        _log.warning("Skipping reference pixel map subtraction.")
        pass
    phase_map.data *= -1

    # Converting phase-map values to channels ------------------------------
    phase_map.data /= sample

    # Converting phase-map from channels to number of points --------------
    phase_map.data = phase_map.data * args.npoints

    # Applying phase-map --------------------------------------------------
    _log.info("")
    _log.info("Applying phase-map:")

    n_channels = data_cube.header['NAXIS3']
    z = np.arange(3 * n_channels) - n_channels
    new_z = np.arange(0, z.size, 1.0 / args.npoints)

    for i in range(m):
        for j in range(n):

            # Extracting a spectrum
            spec = data_cube.data[:, j, i]
            spec = np.hstack((spec, spec, spec))
            dz = phase_map.data[j, i]

            # Re-sample spectrum
            spline = UnivariateSpline(z, spec, s=0.0)
            new_spec = spline(new_z)

            # Cutting spectrum
            new_z = new_z[0:fsr + 1]
            new_spec = new_spec[0:fsr + 1]

            # Shifting spectrum
            new_spec = np.roll(new_spec, int(dz))

            # Under-sampling spectrum
            spline = UnivariateSpline(new_z, new_spec, s=0.0)
            spec = spline(z)

            # Storing new spectrum
            data_cube.data[:, j, i] = spec[n_channels:2 * n_channels]

            # Giving a feedback to the user
            if not args.quiet:
                temp = ((i + 1) * 100.00 / m)
                sys.stdout.write('\r' + 42 * ' ' + '%2.2f%% ' % temp)
                sys.stdout.flush()

    end_of_cube = min(int(round(f_s_r)), data_cube.data.shape[0])
    data_cube.data = data_cube.data[0:end_of_cube, :, :]
    _log.info(" Done.")

    if args.center:
        collapsed_cube = np.mean(data_cube.data, axis=(1, 2))

        collapsed_cube = np.where(
            collapsed_cube > np.percentile(collapsed_cube, 75.),
            collapsed_cube,
            0.
        )

        imax = np.argmax(collapsed_cube)

        _log.info(' Maximum argument found at {:d}'.format(imax))
        _log.info(' Cube center at {:d}'.format(collapsed_cube.size // 2))
        _log.info(' Displacemente to be applied: {:d}'.format(
                imax - collapsed_cube.size // 2))

        data_cube.data = np.roll(data_cube.data,
                                 - (imax - collapsed_cube.size // 2), axis=0)

    # Saving more information in the phase-corrected cube ---------------------
    keys = ['PHMREFX', 'PHMREFY', 'PHMTYPE', 'PHMREFF', 'PHMWCAL', 'PHM_FSR',
            'PHMUNIT', 'PHMSAMP', 'PHMFIT_A', 'PHMFIT_B', 'PHMFIT_C']
    h = phase_map.header

    for key in keys:
        data_cube.header.append(card=(key, h[key]))

    data_cube.header.add_blank('', before='PHMREFX')
    data_cube.header.add_blank('--- PHM Xtractor ---', before='PHMREFX')

    data_cube.header.add_blank(value='', before='PHMFIT_A')
    data_cube.header.add_blank(value='--- PHM Fit ---', before='PHMFIT_A')
    data_cube.header.add_blank(value='f(x) = a * z ** 2 + b * z + c',
                               before='PHMFIT_A')

    # Wavelength Calibration --------------------------------------------------
    collapsed_cube = np.average(data_cube.data, axis=(1, 2))

    collapsed_cube = np.where(
        collapsed_cube > np.percentile(collapsed_cube, 75.),
        collapsed_cube,
        0.
    )

    n_channels = collapsed_cube.size
    imax = signal.argrelmax(collapsed_cube, order=n_channels // 2)[0][0] + 1

    fp_order = 2. * (args.gap_size * 1e-6) / (wavelength * 1e-10)
    fsr_angstrom = (wavelength / fp_order) * (1 / (1 - 1 / fp_order ** 2))
    delta_wavelength = data_cube.header["C3_3"] / data_cube.header["PHM_FSR"] * fsr_angstrom

    _log.info("Reference Channel: {:.2f}".format(imax))
    _log.info("Observed wavelength: {:.2f} A".format(wavelength))
    _log.info("Order: {:.2f}".format(fp_order))
    _log.info("FSR in angstrom: {:.2f}".format(fsr_angstrom))
    _log.info("FSR in BCV: {:.2f}".format(data_cube.header["PHM_FSR"]))
    _log.info("Wavelength per channel: {:5f} A".format(delta_wavelength))

    data_cube.header.set("CRPIX3", imax, after="PHMFIT_C")
    data_cube.header.set("CRVAL3", wavelength, after="CRPIX3")
    data_cube.header.set("C3_3", delta_wavelength, after="CRVAL3")
    data_cube.header.set("CDELT3", delta_wavelength, after="C3_3")

    data_cube.header.add_history(
        'Phase-map corrected using {:s}'.format(map_file), after='PHMFIT_C')
    data_cube.header.add_blank(value='--- phmapply ---', after='PHMFIT_C')
    data_cube.header.add_blank(after='PHMFIT_C')

    # Saving corrected data-cube ----------------------------------------------
    _log.info("Writing output to file %s." % out_file)

    try:
        data_cube.writeto(out_file, overwrite=True)
    except TypeError:
        data_cube.writeto(out_file, clobber=True)

    _log.info("Done.")

    end = time.time() - start
    _log.info("")
    _log.info("Total time ellapsed: {0:02d}:{1:02d}:{2:02d}".format(
            int(end // 3600), int(end % 3600 // 60), int(end % 60)))
    _log.info(" All done!\n")


def shift_spectrum(spec, dz, fsr=-1, sample=1.0, n_points=100):
    """
    Parameters
    ----------
        spec: np.array
            a spectrum to be shifted.

        dz: float
            How big is the shifting.

        fsr: float
            The free-spectra-range in sample units.

        sample: float
            The increment between each channel.

        n_points: int
            Number of points that will be used for super-sampling.
    """
    dz_sign = -np.sign(dz)
    dz = abs(dz) / sample  # From cube units to channels
    dz_points = int(dz * n_points)  # From channels to new sample units

    index = fsr / sample  # From cube units to channels
    index *= n_points  # From channels to new sample units

    if dz_points is 0:
        return spec

    # Get the spectrum from cube
    z = np.arange(spec.size)
    spline = UnivariateSpline(z, spec, s=0.0)

    # Re-sample spectrum
    new_z = np.linspace(z[0], z[-1], z.size * n_points)
    new_spec = spline(new_z)

    # Cutting Spectrum
    new_spec = new_spec[0:fsr]

    # Shifting spectrum
    new_spec = np.roll(new_spec, int(dz_sign * dz_points))

    # Down-sampling
    spline = UnivariateSpline(new_z, new_spec, s=0.0)
    spec = spline(z)

    return spec
