#!/usr/bin/env python 
# -*- coding: utf8 -*-
from __future__ import division, print_function

__author__ = 'Bruno Quint'

import os

from matplotlib import pyplot as plt
from matplotlib import gridspec

from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.table import Table
from astropy.visualization import ImageNormalize, LinearStretch, ZScaleInterval
from astropy.wcs import WCS

from astroquery.sdss import SDSS
from astroquery.simbad import Simbad
from astroquery.ned import Ned

fits_file = '/home/bquint/Data/2016-11-30/RED/amzfSO2016B-015_1130.082.fits'
hdu = fits.open(fits_file)[0]
hdu.header['EQUINOX'] = 2000

wcs = WCS(hdu.header)
norm = ImageNormalize(hdu.data, interval=ZScaleInterval(99), stretch=LinearStretch())

gs = gridspec.GridSpec(2, 1, height_ratios=[8, 2])
fig = plt.figure()

ax1 = fig.add_subplot(gs[0], projection=wcs)
ax1.imshow(hdu.data, origin='lower', cmap='cubehelix', norm=norm)
ax1.set_xlabel('RA')
ax1.set_ylabel('Dec')
ax1.set_xlim(0, hdu.data.shape[0])
ax1.set_ylim(0, hdu.data.shape[1])

c = SkyCoord(ra=hdu.header['CRVAL1'] * u.deg, dec=hdu.header['CRVAL2'] * u.deg)
s = c.to_string('hmsdms')
hdu.header['CALC_COO'] = c.to_string('hmsdms')
hdu.header['CALC_COO'] = hdu.header['CALC_COO'].replace('h', ':')
hdu.header['CALC_COO'] = hdu.header['CALC_COO'].replace('d', ':')
hdu.header['CALC_COO'] = hdu.header['CALC_COO'].replace('m', ':')
hdu.header['CALC_COO'] = hdu.header['CALC_COO'].replace('s', '')

s = 'Object Name: {OBJECT:s}\n' \
    'Target Coords: {RA:s} {DEC:s} \n' \
    'Coords Found: {CALC_COO:s}'.format(**hdu.header)

ax2 = fig.add_subplot(gs[1])
ax2.text(0.05, 0.5, s, va='center', ha='left')
ax2.set_xticks([])
ax2.set_yticks([])

plt.tight_layout()
plt.show()



# r = 3 * u.arcmin
# print(c)
#
# region = Ned.query_region(coordinates=c, radius=r)
# region = SDSS.query_region(coordinates=c, radius=r)
#
# for obj in region:
#     obj_coord = SkyCoord(ra=obj['RA(deg)'] * u.deg, dec=obj['DEC(deg)'] * u.deg)
#     x, y = obj_coord.to_pixel(wcs)
#     print(x, y)
#     plt.scatter(x, y, edgecolor='None', facecolor='red', marker='o')
