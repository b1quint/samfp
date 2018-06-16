#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ccdproc
import glob
import os


from astropy.io import fits as pyfits
from samfp.xjoin import SAMI_XJoin
from samfp import image_combine

PATH = "/Users/Bruno/Data/SAM/20180614"
KEYWORDS = ["OBSTYPE", "FILTERS", "CCDSUM"]


def main():

    xjoin = SAMI_XJoin()

    os.makedirs(os.path.join(PATH, "RED"), exist_ok=True)
    list_of_files = glob.glob(os.path.join(PATH, '*.fits'))

    table = []
    for _file in list_of_files:

        try:
            hdu = pyfits.open(_file)
        except OSError:
            print("[W] Could not read file: {}".format(_file))
            continue

        row = {
            'filename': _file,
            'obstype': hdu[0].header['obstype'],
            'filter_id': hdu[0].header['filters'],
            'binning': [
                int(b) for b in hdu[1].header['ccdsum'].strip().split(' ')]
        }

        table.append(row)

    list_of_binning = []
    for row in table:
        if row['binning'] not in list_of_binning:
            list_of_binning.append(row['binning'])

    for binning in list_of_binning:

        sub_table = [row for row in table if row['binning'] == binning]

        zero_table = [row for row in sub_table if row['obstype'] == 'ZERO']
        dflat_table = [row for row in sub_table if row['obstype'] == 'DFLAT']
        sflat_table = [row for row in sub_table if row['obstype'] == 'SFLAT']
        obj_table = [row for row in sub_table if row['obstype'] == 'OBJECT']

        zero_files = [r['filename'] for r in zero_table]
        zero_list_name = os.path.join(
            PATH, "RED", "0Zero{}x{}".format(binning[0], binning[1]))

        with open(zero_list_name, 'w') as zero_list_buffer:
            zero_list_buffer.write('\n'.join(zero_files))

        for zero_file in zero_files:
            zero_data = xjoin.get_joined_data(zero_file)
            zero_header = pyfits.getheader(zero_file)
            path, fname = os.path.split(zero_file)
            zero_file = os.path.join(path, 'RED', fname)
            pyfits.writeto(zero_file, zero_data, zero_header)

        ic = ccdproc.ImageFileCollection(
            location=os.path.join(PATH, 'RED'),
            glob_include='*.fits',
            keywords=KEYWORDS
        )

        zero_combine_files = [
            os.path.join(PATH, 'RED', f)
            for f in ic.files_filtered(obstype='ZERO')
        ]

        master_zero_fname = os.path.join(PATH, 'RED', zero_list_name + '.fits')

        zero_combine = image_combine.ZeroCombine(
            input_list=zero_combine_files,
            output_file=master_zero_fname
        )

        zero_combine.run()






if __name__ == '__main__':
    main()