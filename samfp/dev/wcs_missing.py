#!/usr/bin/env python 
# -*- coding: utf8 -*-
from __future__ import division, print_function

__author__ = 'Bruno Quint'

import os
import pandas

from astropy import log
from astropy.io import fits
from ccdproc import ImageFileCollection
from glob import glob

path = '/home/bquint/Data/2016-11-29/RED/'
file_pattern = '*SO2016B-015*.fits'

keys = ['RA', 'DEC']

list_of_files = glob(os.path.join(path, file_pattern))
list_of_files = [os.path.split(f)[-1] for f in list_of_files]
list_of_files.sort()

list_with_asol = [f[1:] for f in list_of_files if f[0] == 'a']
list_wout_asol = [f for f in list_of_files if not f[0] == 'a']

data_frame = pandas.DataFrame(columns=['Column_wout', 'Column_with', 'Object'])

for f in list_wout_asol:

    h = fits.getheader(os.path.join(path, f))

    d = {}
    d['Column_wout'] = f
    d['Column_with'] = f if f in list_with_asol else None
    d['Object'] = h['object']

    s = pandas.Series(data=d)
    data_frame = data_frame.append(s, ignore_index=True)

#print(data_frame)
print(data_frame[data_frame.isnull().any(axis=1)])



