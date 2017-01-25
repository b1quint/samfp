#!/usr/bin/env python 
# -*- coding: utf8 -*-

from __future__ import division, print_function

import sqlite3

__author__ = 'Bruno Quint'

class SAMI_Pipe:

    path = '/home/bquint/Data/SAMFP/20160930'
    database_name = 'temp.db'
    table_name = '20160930'

    def __init__(self):
        load_database(self.database_name)


    def __call__(self, *args, **kwargs):
        print('Done')


def load_database(db_name):
    """
    Load a sqlite database.

    Parameters
    ----------
    db_name

    Returns
    -------
    c : sqlite3.Cursor

    """
    conn = sqlite3.connect(db_name)
    c = conn.cursor('CREATE TABLE IF NOT EXISTS {:table_name} '
        'ndim INT'
        'filename STRING, '
        'object STRING, '
        'obstype STRING, '
        'notes STRING, '
        'exptime FLOAT, '
        'darktime FLOAT, '
        'radecsys STRING, '
        'radeceq FLOAT, '
        'ra STRING, '
        'dec STRING,'
        'timesys STRING, '
        'dateobs STRING'
        'timeobs STRING'
        'fp_id STRING'
        'fp_channel STRING'
        'fp_z STRING'
        'datared_bias BOOL'
        'datared_dark BOOL'
        'datared_flat BOOL'
    )




if __name__ == '__main__':

    sami_pipe = SAMI_Pipe()
    sami_pipe()