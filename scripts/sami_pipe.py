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
            data = xjoin.get_joined_data(zero_file)
            header = pyfits.getheader(zero_file)

            data, header, prefix = xjoin.join_and_process(data, header)

            path, fname = os.path.split(zero_file)
            zero_file = os.path.join(path, 'RED', fname)
            pyfits.writeto(zero_file, data, header)

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

        flat_table = sflat_table + dflat_table
        filters_used = []
        for row in flat_table:
            if row['filter_id'] not in filters_used:
                filters_used.append(row['filter_id'])

        for _filter in filters_used:

            sub_table_by_filter = [
                row for row in flat_table if row['filter_id'] == _filter
            ]

            flat_list_name = os.path.join(
                PATH, 'RED',
                "1FLAT_{}x{}_{}".format(binning[0], binning[1], _filter)
            )

            flat_files = [row['filename'] for row in sub_table_by_filter]

            with open(flat_list_name, 'w') as flat_list_buffer:
                flat_list_buffer.write('\n'.join(flat_files))

            for flat_file in flat_files:

                xjoin.bias_file = master_zero_fname
                d = xjoin.get_joined_data(flat_file)
                h = pyfits.getheader(flat_file)

                d, h, p = xjoin.join_and_process(d, h)

                path, fname = os.path.split(flat_file)
                flat_file = os.path.join(path, 'RED', fname)
                pyfits.writeto(flat_file, d, h)

            master_flat_fname = os.path.join(PATH, 'RED',
                                             flat_list_name + '.fits')

            flat_combine_files = [
                os.path.join(PATH, 'RED', os.path.split(f)[-1])
                for f in flat_files
            ]

            flat_combine = image_combine.FlatCombine(
                 input_list=flat_combine_files,
                 output_file=master_flat_fname
            )

            flat_combine.run()

            sub_table_by_filter = [
                row for row in obj_table if row['filter_id'] == _filter
            ]

            obj_list_name = os.path.join(
                PATH, 'RED',
                "2OBJECT_{}x{}_{}".format(binning[0], binning[1], _filter)
            )

            obj_files = [row['filename'] for row in sub_table_by_filter]

            with open(obj_list_name, 'w') as obj_list_buffer:
                obj_list_buffer.write('\n'.join(obj_files))

            for obj_file in obj_files:

                xjoin.bias_file = master_zero_fname
                xjoin.flat_file = master_flat_fname
                d = xjoin.get_joined_data(obj_file)
                h = pyfits.getheader(obj_file)

                d, h, p = xjoin.join_and_process(d, h)

                path, fname = os.path.split(obj_file)
                obj_file = os.path.join(path, 'RED', fname)
                pyfits.writeto(obj_file, d, h)


if __name__ == '__main__':
    main()