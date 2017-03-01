#!/usr/bin/env python 
# -*- coding: utf8 -*-
from __future__ import division, print_function

import matplotlib.pyplot as plt
import numpy as np
import os

from astropy.io import fits
from astropy.stats import sigma_clipped_stats
from astropy.visualization import LogStretch, PercentileInterval
from astropy.visualization.mpl_normalize import ImageNormalize
from astropy.wcs import WCS
from photutils import DAOStarFinder
from photutils import CircularAperture
from scipy import ndimage

__author__ = 'Bruno Quint'


def main():

    # Initial setup ---
    path = '/Users/Bruno/PycharmProjects/samfp/sample_data/'
    filename = 'mzfSO2016B-015_1129.140.fits'
    radius = 15
    threshold = 5.

    # Read data and blur it ---
    data = fits.getdata(os.path.join(path, filename))

    # Read and fix header before using it ---
    header = fits.getheader(os.path.join(path, filename))
    header['equinox'] = 2000.
    header['RADESYSa'] = header['RADECSYS']
    del header['RADECSYS']

    # Get some statistics ---
    mean, median, std = sigma_clipped_stats(data, sigma=3.0)
    print(
        "\n"
        "Filename: {}\n"
        " Mean Value: {:.2f}\n"
        " Median Value: {:.2f}\n"
        " STD Value: {:.2f}".format(filename, mean, median, std)
    )

    # Find sources ---
    daofind = DAOStarFinder(fwhm=radius, threshold=threshold * std)
    sources = daofind(data - median)
    nfound = len(sources)
    print(" {:d} sources found".format(nfound))

    # Clean duplicated sources ---
    n_new = len(sources)
    n_old = None

    while n_new != n_old:

        for i in range(len(sources)):

            x = sources[i]['xcentroid'] - sources['xcentroid']
            y = sources[i]['ycentroid'] - sources['ycentroid']
            r = np.sqrt(x ** 2 + y ** 2)
            s = (r > 0) * (r < 10.)  # Is there someone close but it is not me?

            if s.any():

                mean_x = np.mean(sources[s + (r == 0)]['xcentroid'])
                mean_y = np.mean(sources[s + (r == 0)]['ycentroid'])

                sources[i]['xcentroid'] = mean_x
                sources[i]['ycentroid'] = mean_y

                sources = sources[~s]
                break

        n_old = n_new
        n_new = len(sources)

    print(" {:d} sources kept".format(n_new))

    positions = (sources['xcentroid'], sources['ycentroid'])
    apertures = CircularAperture(positions, r=radius)

    norm = ImageNormalize(interval=PercentileInterval(90), stretch=LogStretch())
    wcs = WCS(header)
    plt.subplot(111, projection=wcs)
    plt.imshow(data, norm=norm, origin='lower', cmap='gray')

    apertures.plot(color='red', lw=1.5, alpha=0.5)
    plt.show()


if __name__ == '__main__':
    main()

