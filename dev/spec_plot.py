#!/usr/bin/env python 
# -*- coding: utf8 -*-

from __future__ import division, print_function

import numpy as np

from astropy.io import fits as pyfits
from astropy.modeling import models
from astropy.modeling import fitting
from matplotlib import pyplot as plt
from scipy import interpolate
from scipy import signal

__author__ = 'Bruno Quint'

# Input Definition
i = 0
inputs = {
    'files': ['/home/bquint/Data/SAMFP/20161123/002/spec.fits',
              '/home/bquint/Data/SAMFP/20161123/003/spec.fits',
              '/home/bquint/Data/SAMFP/20161123/004/spec.fits',
              '/home/bquint/Data/SAMFP/20161123/005/spec.fits',
              '/home/bquint/Data/SAMFP/20161123/006/spec.fits',
              '/home/bquint/Data/SAMFP/20161123/007/spec.fits'
              ],
    'comments': ['FP Parallel', 'x-fine = 2.0', 'y-fine = 2.6',
                 'y-fine = 1.6', 'FSR scanned', 'More than FSR scanned'
                 ]
}

title = 'SAMFP SV2016B 2016-11-23\nSpectrum at the center of the rings\n' \
        'spec{:03d}.fits - {:s}'


def main():

    for i in range(6):
        filename = inputs['files'][i]

        # Read file
        header = pyfits.getheader(filename)
        spec = pyfits.getdata(filename)
        z = get_z(header)

        # Plot the raw data
        fig = plt.figure(1)
        ax = fig.add_subplot(111)
        ax.set_title(title.format(i + 2, inputs['comments'][i]))
        ax.set_xlabel('z [bcv]')
        ax.set_ylabel('Intensity [counts]')
        ax.set_xlim(z[0], z[-1])
        ax.set_ylim(
            ymin=spec.min() - 0.05 * spec.ptp(),
            ymax=spec.max() + 0.15 * spec.ptp()
        )

        p1, = ax.plot(z, spec, 'o', color='black')

        # Find maximum
        foo = np.where(
            np.abs(spec > spec.min() + 0.75 * spec.max()), spec, 0
        )
        maxima = signal.argrelmax(foo, axis=0, order=10)[0]
        for m in maxima:
            ax.axvline(x=z[m], linestyle=':', color='k', alpha=0.5)

        # Lorentzian Modeling
        new_z = np.linspace(z[0], z[-1], 1000)
        lmodel = models.Lorentz1D()
        lmodels = []
        fitter = fitting.LevMarLSQFitter()
        for m in maxima:
            lmodel.x_0 = z[m]
            lmodel.amplitude = spec[m]
            f = fitter(lmodel, z, spec)
            p2, = ax.plot(new_z, f(new_z), 'k-', alpha=0.75)
            lmodels.append(f)

        # Gaussian Modeling
        new_z = np.linspace(z[0], z[-1], 1000)
        g_model = models.Gaussian1D()
        gmodels = []
        fitter = fitting.LevMarLSQFitter()
        for m in maxima:
            g_model.mean = z[m]
            g_model.amplitude = spec[m]
            f = fitter(g_model, z, spec)
            p3, = ax.plot(new_z, f(new_z), 'k--', alpha=0.5)
            gmodels.append(f)

        # Set labels
        lgd = ax.legend(
            (p1, p2, p3), ('Science data', 'Lorentzian fit', 'Gaussian fit'),
            loc='upper right', bbox_to_anchor=(1.0, -0.1)
        )

        # Show fit parameters
        if len(maxima) is 1:
            foo = 'Lorentzian FWHM: {:0.2f} bcv\n' \
                  'Gaussian FWHM: {:0.2f} bcv\n' \
                  'Center at: {:0.2f} bcv'
            l_fwhm = lmodels[0].fwhm.value
            g_fwhm = gmodels[0].stddev.value
            center = lmodels[0].x_0.value
            fig.text(
                0.1, -0.1, foo.format(l_fwhm, g_fwhm, center),
                bbox={'facecolor': 'white', 'pad': 10},
                horizontalalignment='left'
            )
        elif len(maxima) is 2:
            foo = 'Lorentzian FWHM: {:0.2f} bcv\n' \
                  'Gaussian FWHM: {:0.2f} bcv\n' \
                  'FSR: {:0.2f} bcv'
            l_fwhm = (lmodels[0].fwhm.value + lmodels[1].fwhm.value) * 0.5
            g_fwhm = (gmodels[0].stddev.value + gmodels[1].stddev.value) * 0.5
            center = abs(lmodels[0].x_0.value - lmodels[1].x_0.value)
            fig.text(
                0.1, -0.1, foo.format(l_fwhm, g_fwhm, center),
                bbox={'facecolor': 'white', 'pad': 10},
                horizontalalignment='left'
            )

        # Save figure
        fig.savefig(
            'spec{:03d}'.format(i + 2), bbox_extra_artists=(lgd,),
            bbox_inches='tight'
        )
        fig.clear()


def get_z(h):
    """
    Parameters
    ----------
    h

    Returns
    -------

    """
    z = np.arange(h['NAXIS1'])
    z = (z + 1 - h['CRPIX1']) * h['CDELT1'] + h['CRVAL1']
    return z

if __name__ == '__main__':
    main()