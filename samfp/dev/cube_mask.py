#!/usr/bin/env python 
# -*- coding: utf8 -*-
from __future__ import division, print_function

__author__ = 'Bruno Quint'

import cv2
import os
import numpy as np

from matplotlib import pyplot as plt
from matplotlib import gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable
from numpy import ma

from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.table import Table
from astropy.visualization import ImageNormalize, LinearStretch, ZScaleInterval
from astropy.wcs import WCS

filename = '/home/bquint/Data/SAMFP/20161124/004/cube.fits'
cube = fits.getdata(filename)

data = np.median(cube, axis=0)
del cube

gs = gridspec.GridSpec(1, 2)
fig = plt.figure(figsize=(20, 10))

norm = ImageNormalize(data, interval=ZScaleInterval(99),
                      stretch=LinearStretch())
Z = np.array(norm(data) * 255, dtype=np.uint8)
blur = cv2.GaussianBlur(Z, (25, 25), 0)
ret, th = cv2.threshold(blur, 0, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
Zm = ma.masked_where(th == 1, th)

palette = plt.cm.gray
palette.set_bad('r', 0.25)

ax2 = fig.add_subplot(gs[1])
ax2.set_xlabel('')
ax2.set_ylabel('')
ax2.set_xlim(0, data.shape[0])
ax2.set_ylim(0, data.shape[1])

im = ax2.imshow(data, origin='lower', cmap='viridis',
                interpolation='nearest', norm=norm)

ax1 = fig.add_subplot(gs[0])
ax1.hist(data.ravel(), bins=100, log=True, alpha=0.5)
ax1.hist((data * th)[th > 0].ravel(), bins=100, log=True, alpha=0.5)
ax2.imshow(Zm, interpolation='nearest', cmap=palette, origin='lower')

divider = make_axes_locatable(ax2)
cax2 = divider.append_axes('right', size='5%', pad=0.05)
cbar = fig.colorbar(im, cax=cax2)

plt.show()

# cube = fits.getdata(filename)
# header = fits.getheader(filename)
# for k in range(cube.shape[0]):
#     temp = cube[k]
#     a = ma.median(ma.masked_where(th == 1, temp))
#     b = ma.median(ma.masked_where(th == 0, temp))
#     print(k, a, b)
#     cube[k] -= (b - a) * (th * norm(data))
#
# fits.writeto(filename.replace('.fits', '_masked.fits'), cube, header, overwrite=True)
