#!/usr/bin/env python 
# -*- coding: utf8 -*-
"""
    x2d Collapsed

    Display the 2D collapsed data-cube.

    by Bruno Quint
"""

from __future__ import division, print_function
from astropy.io import fits as pyfits
from astropy import visualization as viz
from matplotlib.lines import Line2D
from scipy.ndimage import median_filter

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import os

__author__ = 'Bruno Quint'

# Global setup ---
CM_PER_INCH = 2.54
SAMI_PLATE_SCALE = 0.0455 * 4

# Define style ---
plt.style.use('seaborn-talk')
mpl.rcParams['image.cmap'] = 'cubehelix'
mpl.rcParams['image.interpolation'] = 'nearest'
mpl.rcParams['image.origin'] = 'lower'
mpl.rcParams['xtick.labelsize'] = 0
mpl.rcParams['ytick.labelsize'] = 0

def main():

    # Inputs ---
    path = '/home/bquint/Dropbox/SAM-FP/2017-03-01/NGC2818'
    filename = 'NGC2818_2D.fits'

    x0 = 150
    xf = 750
    y0 = 150
    yf = 550

    # Load data ---
    data = pyfits.getdata(os.path.join(path, filename))
    data = data[y0:yf,x0:xf]
    data = median_filter(data, 5)


    # Get some statistics ---
    avg = np.mean(data)
    med = np.median(data)
    std = np.std(data)

    print("\n Mean: {:.2f}".format(avg) +
          "\n Median: {:2f}".format(med) +
          "\n STD: {:2f}".format(std))

    # Display data ---
    vmin = med - 0.5 * std
    vmax = med + 8 * std

    norm = viz.ImageNormalize(
        data,
        stretch=viz.LinearStretch(),
        vmin=vmin,
        vmax=vmax
        )

    fig = plt.figure(figsize=(8, 8))

    ax1 = fig.add_subplot(111)
    ax1.imshow(data, norm=norm)

    # Add pixel scale ruler ---
    x = 0.8 * data.shape[1]
    y = 0.1 * data.shape[0]
    ax1.text(x, y, '30 arcsec', color='w', ha='center', va='bottom')

    width = 30 / SAMI_PLATE_SCALE # arcsec to pixels
    xmin = x - width // 2
    xmax = x + width // 2
    l1 = Line2D([xmin, xmax], [y, y], color='w', linewidth=2)
    ax1.add_line(l1)

    plt.show()
    plt.savefig(os.path.join(path, filename.replace('.fits', '.png')))


def cm2in(wh):
    """Convert a tuple from centimeters to inches.

    Parameters
    -----------
        wh : tuple
            A tuple containing the width and the height of a figure in cm to be
            converted to inches.

    Returns
    -------
        wh_in : tuple
            A tuple containing the width and the height of a figures converted
            to inches.
    """
    wh_in = tuple(x / CM_PER_INCH for x in wh)
    return wh_in


if __name__ == '__main__':
    main()