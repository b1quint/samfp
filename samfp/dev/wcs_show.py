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

fits_file = '/home/bquint/Data/2016-11-29/RED/amzfSO2016B-015_1129.264.fits'
hdu = fits.open(fits_file)[0]
h = hdu.header
h['EQUINOX'] = 2000

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

c = SkyCoord(ra=h['CRVAL1'] * u.deg, dec=h['CRVAL2'] * u.deg)
c = c.from_pixel(h['NAXIS1'] // 2, h['NAXIS2'] // 2, wcs=wcs, origin=0)
s = c.to_string('hmsdms')
h['CALC_COO'] = c.to_string('hmsdms')
h['CALC_COO'] = h['CALC_COO'].replace('h', ':')
h['CALC_COO'] = h['CALC_COO'].replace('d', ':')
h['CALC_COO'] = h['CALC_COO'].replace('m', ':')
h['CALC_COO'] = h['CALC_COO'].replace('s', '')

s = 'Object Name: {OBJECT:s}\n' \
    'Target Coords: {RA:s} {DEC:s} \n' \
    'Coords Found: {CALC_COO:s}'.format(**hdu.header)

ax2 = fig.add_subplot(gs[1])
ax2.text(0.05, 0.5, s, va='center', ha='left')
ax2.set_xticks([])
ax2.set_yticks([])

r = 3 * u.arcmin
region = Ned.query_region(coordinates=c, radius=r)
region = region.to_pandas()
print(region)

# for obj in region:
#     obj_coord = SkyCoord(ra=obj['RA(deg)'] * u.deg, dec=obj['DEC(deg)'] * u.deg)
#     x, y = obj_coord.to_pixel(wcs)
#     ax1.scatter(x, y, edgecolor='None', facecolor='red', marker='o')
#
# plt.tight_layout(pad=1.3, w_pad=2)
# plt.show()




