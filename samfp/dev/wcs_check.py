#!/usr/bin/env python 
# -*- coding: utf8 -*-
from __future__ import division, print_function

import glob
import os

from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.wcs import WCS

__author__ = 'Bruno Quint'

path = '/home/bquint/Data/2016-12-01/RED'
pattern = 'amzf*.fits'

list_of_files = glob.glob(os.path.join(path, pattern))
list_of_files.sort()

for f in list_of_files:
    h = fits.getheader(f)
    h['EQUINOX'] = 2000.
    h['FILENAME'] = f

    c = SkyCoord(ra=h['CRVAL1'] * u.deg, dec=h['CRVAL2'] * u.deg)

    wcs = WCS(h)
    c = c.from_pixel(h['NAXIS1'] // 2, h['NAXIS2'] // 2, wcs=wcs, origin=1)
    s = c.to_string('hmsdms')
    h['COORDS'] = c.to_string('hmsdms')
    h['COORDS'] = h['COORDS'].replace('h', ':')
    h['COORDS'] = h['COORDS'].replace('d', ':')
    h['COORDS'] = h['COORDS'].replace('m', ':')
    h['COORDS'] = h['COORDS'].replace('s', '')
    h['RA_FOUND'] = h['COORDS'].split(' ')[0]
    h['DEC_FOUND'] = h['COORDS'].split(' ')[1]

    s = "{FILENAME:60s}\t\t" \
        "{OBJECT:15s}\t\t" \
        "{RA:15s}\t" \
        "{DEC:15s}\t" \
        "{RA_FOUND:15s}\t" \
        "{DEC_FOUND:15s}".format(**h)

    print(s)