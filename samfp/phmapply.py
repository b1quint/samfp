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

from .tools import io, version

log = io.MyLogger(__name__)


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
        '-s', '--speed', type=float, default=0.0,
        help="Systemic velocity to be applied to the emitted wavelength [km/s]."
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

    args = parser.parse_args()
    log.set_verbose(verbose=not args.quiet)

    # Printing program header --------------------------------------------------
    start = time.time()
    log.info("")
    log.info("SAM-FP Tools: PHase-Map Apply")
    log.info("by Bruno Quint (bquint@ctio.noao.edu)")
    log.info("version {:s}".format(version.__str__))
    log.info("Starting program.")
    log.info("")

    root_dir = os.path.dirname(args.cube_file)
    cube_file = args.cube_file
    map_file = args.map_file

    if args.output is None:
        out_file = 'phc_' + os.path.split(args.cube_file)[-1]
    else:
        out_file = args.output

    log.info("Root dir: %s" % root_dir)
    log.info("Cube to be corrected: %s" % cube_file)
    log.info("Phase-map to be applied: %s" % map_file)
    log.info("Output corrected cube: %s" % out_file)

    # Systemic wavelength ------------------------------------------------------
    vel = args.speed
    c = 299792 # km/s
    wavelength = args.wavelength * np.sqrt((1 + vel / c) / (1 - vel / c))

    log.info("")
    log.info("Emitted/systemic wavelength: %.2f A" % args.wavelength)
    log.info("Systemic velocity: %.2f km/s" % vel)
    log.info("Observed wavelength: %.2f A" % wavelength)

    # Reading input data ------------------------------------------------------
    log.info("")
    log.info("Reading cube to be corrected.")
    data_cube = pyfits.open(cube_file)[0]
    log.info("Done.")

    log.info("Reading phase-map to be applied.")
    phase_map = pyfits.open(map_file)[0]
    log.info("Done.")

    # Checking data -----------------------------------------------------------
    if data_cube.data[0].shape != phase_map.shape:
        log.error("Cube and map does not have matching width and height.")
        log.error("[!] Leaving now.\n")
        sys.exit()

    if data_cube.data.ndim != 3:
        log.error("[!] Cube file is not really a cube.")
        log.error("[!] Leaving now.\n")
        sys.exit()

    if phase_map.data.ndim != 2:
        log.error("[!] Map file is not really an image.")
        log.error("[!] Leaving now.\n")
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
        log.error('"CDELT3" keyword was not found in the header.')
        sample = 1

    # Reading the Free-Spectral-Range --------------------------------------
    try:
        log.info("")
        log.info("Reading free-spectral-range from cube header.")
        # TODO add an option to use the FSR found while extracting
        # TODO the phase-map or while fitting it.
        # TODO or even to give the option for the user to enter it.
        cal_fsr = phase_map.header['PHM_FSR']
        cal_wavelength = phase_map.header['PHMWCAL']
        f_s_r = cal_fsr / cal_wavelength * wavelength
        log.info(" Free Spectral Range = %.2f %s" % (f_s_r, units))

    except KeyError:
        log.info("Please, enter the free-spectral-range in %s units" % units)
        f_s_r = io.input("    >")

    f_s_r = round(f_s_r / abs(sample)) # From BCV to Channels
    log.info("Free-Spectral-Range is %d channels" % f_s_r)

    fsr = f_s_r * args.npoints  # From Channels to nPoints
    fsr = int(round(fsr))
    log.info("Free-Spectral-Range is %d points" % fsr)

    # Assure that the reference spectrum will not be moved ----------------
    try:
        phase_map.data = phase_map.data - phase_map.data[ref_y, ref_x]
    except IndexError:
        log.warn("Reference pixel out of field.")
        log.warn("Skipping reference pixel map subtraction.")
        pass
    phase_map.data *= -1

    # Converting phase-map values to channels ------------------------------
    phase_map.data /= sample

    # Converting phase-map from channels to number of points --------------
    phase_map.data = phase_map.data * args.npoints

    # Applying phase-map --------------------------------------------------
    log.info("")
    log.info("Applying phase-map:")

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
                sys.stdout.write('\r    %2.2f%% ' % temp)
                sys.stdout.flush()

    end_of_cube = min(int(round(f_s_r)), data_cube.data.shape[0])
    data_cube.data = data_cube.data[0:end_of_cube, :, :]
    log.info(" Done.")

    if args.center:
        collapsed_cube = data_cube.data.sum(axis=2).sum(axis=1)
        imax = np.argmax(collapsed_cube)
        print(' Maximum argument found at {:d}'.format(imax))
        print(' Cube center at {:d}'.format(collapsed_cube.size // 2))
        print(' Displacemente to be applied: {:d}'.format(imax - collapsed_cube.size // 2))
        data_cube.data = np.roll(data_cube.data, - (imax - collapsed_cube.size // 2), axis=0)

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

    # data_cube.header.add_history(
    #     'Phase-map corrected using {:s}'.format(map_file), after='PHMFIT_C'
    # )
    # data_cube.header.add_blank(value='--- phmapply ---', after='PHMFIT_C')
    # data_cube.header.add_blank(after='PHMFIT_C')

    # Saving corrected data-cube ----------------------------------------------
    log.info("Writing output to file %s." % out_file)

    try:
        data_cube.writeto(out_file, overwrite=True)
    except TypeError:
        data_cube.writeto(out_file, clobber=True)

    log.info("Done.")

    end = time.time() - start
    log.info("")
    log.info("Total time ellapsed: {0:02d}:{1:02d}:{2:02d}".format(
            int(end // 3600), int(end % 3600 // 60), int(end % 60)))
    log.info(" All done!\n")


# Method shift_spectrum ========================================================
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
