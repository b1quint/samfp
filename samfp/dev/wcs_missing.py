#!/usr/bin/env python 
# -*- coding: utf8 -*-
from __future__ import division, print_function

__author__ = 'Bruno Quint'

import numpy as np
import os
import pandas

from astropy import log
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.wcs import WCS
from glob import glob

path = '/home/bquint/Data/2016-12-02/RED/'
file_pattern = '*SO2016B-015*.fits'

list_of_files = glob(os.path.join(path, file_pattern))
list_of_files = [os.path.split(f)[-1] for f in list_of_files]
list_of_files.sort()

list_with_asol = [f[1:] for f in list_of_files if f[0] == 'a']
list_wout_asol = [f for f in list_of_files if not f[0] == 'a']

data_frame = pandas.DataFrame(columns=['Column_wout', 'Column_with', 'Object', 'RA', 'DEC', 'Center_Coods'])

for f in list_wout_asol:

    # Read and fix header before using it ---
    h = fits.getheader(os.path.join(path, f))
    h['equinox'] = 2000.
    h['RADESYSa'] = h['RADECSYS']
    del h['RADECSYS']

    # Create WCS using header ---
    wcs = WCS(h)

    # Getting the coordinates of the center of the field ---
    c_center = wcs.wcs_pix2world(h['naxis1'] // 2, h['naxis2'] // 2, 0)
    c_center = SkyCoord(ra=c_center[0] * u.deg, dec=c_center[1] * u.deg)

    # Create dictionary to populate data frame ---
    d = {}
    d['Column_wout'] = f
    d['Column_with'] = f if f in list_with_asol else None
    d['Object'] = h['object']
    d['RA'] = h['RA']
    d['DEC'] = h['DEC']
    d['Center_Coods'] = c_center.to_string('hmsdms', sep=':', precision=3)

    # Populate data frame ---
    s = pandas.Series(data=d)
    data_frame = data_frame.append(s, ignore_index=True)

df = data_frame[data_frame.isnull().any(axis=1)]
df.to_csv(os.path.join(path, 'failed_astrometry.csv'))



