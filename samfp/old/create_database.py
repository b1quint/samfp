#!/usr/bin/env python2
from __future__ import print_function, division

import argparse
import logging
import os
import signal
import sqlite3 as lite
import sys
import warnings

from astropy.io import fits as pyfits
from astropy.utils.exceptions import AstropyUserWarning
from ccdproc import ImageFileCollection
from glob import glob
from multiprocessing import Pool

# Setting log
logging.captureWarnings(False)
log_fmt = logging.Formatter()
log_handler = logging.StreamHandler()
log_handler.setFormatter(log_fmt)
log = logging.getLogger(__name__)
log.addHandler(log_handler)
log.setLevel(logging.NOTSET)

# Make warnings run as exceptions
warnings.filterwarnings('error')


def signal_handler(signal, frame):
    sys.exit()


def files_to_database(path, keys, cursor):
    """
    Read the images inside the path and add their information to a table 
    inside a data-base accessed by the connector.
    
    Parameters:
        path : str
            The path where we will walk looking for fits files
        keys : dict
            A dictionary with the keys that will be looked for in the headers.
        cursor : sqlite.Cursor
            A SQLite Cursor that will receive the rows.
    """

    if not os.path.exists(path):
        raise (IOError, 'Could not open file: {:s}'.format(path))

    if not isinstance(keys, dict):
        raise (TypeError, '"keys" should be a dictionary. '
                          'Found {:s} instead'.format(keys.__class__))

    if not isinstance(cursor, lite.Cursor):
        raise (TypeError, '"cursor" should be a sqlite. Cursor object. '
                          'Found {:s} instead.'.format(str(cursor.__class__)))

    list_of_files = glob(os.path.join(path, '*', '*.fits'))
    list_of_files.sort()

    for filename in list_of_files:
        file_to_database(filename, keys, cursor)

    return


def file_to_database(filename, keys, cursor):
    """
    Save the information from a header based on the keys to a table
    inside a data-base accessed by the connector.

    Parameters:
        filename : str
            The filename from where this method will extract information.
        keys : dict
            A dictionary with the keys that will be looked for in the headers.
        cursor : sqlite.Cursor
            A SQLite Cursor that will receive the rows.
    """
    try:
        hdu_list = pyfits.open(filename)
    except (IOError, Warning) as err:
        log.warning(' %s : %s' % (err.args[0], filename))
        return

    header = hdu_list[0].header
    s = 'INSERT INTO my_table ('
    for k in keys:
        s += '{}, '.format(k)
    s = s[:-2] + ') VALUES ('

    for k in keys:
        if k not in header:
            s += "NULL, "
            continue
        if isinstance(header[k], str):
            s += "'{}', ".format(header[k])
        elif isinstance(header[k], float):
            s += '{}, '.format(header[k])

    s = s[:-2] + ');'

    log.debug(s)
    cur.execute(s)


def fix_header(filename):
    """
    Fix the header of a single image obtained with SAM and SAMI by removing the
    'ADC' card.

    Parameters
    ----------
        filename : str
            full path that contains an FITS image.
    """

    try:
        hdu_list = pyfits.open(filename)
    except (IOError, Warning) as err:
        log.warning(' %s : %s' % (err.args[0], filename))
        return

    for hdu in hdu_list:
        try:
            del hdu.header['ADC']
        except KeyError:
            log.debug('Ignoring file: %s' % filename)
            return

    log.debug('Updating file: %s' % filename)
    hdu_list.writeto(filename, clobber=True)
    return


def fix_headers(path):
    """
    Fix the header of images contained in the path that were obtained with SAM
    and SAMI by removing the 'ADC' card.

    Parameters
    ----------
        path : str
            full path that contains FITS images.
    """
    list_of_files = glob(os.path.join(path, '*', '*.fits'))
    list_of_files.sort()

    p = Pool(10)
    try:
        p.map_async(fix_header, list_of_files).get(99999999)
    except KeyboardInterrupt:
        log.warning('\n\nYou pressed Ctrl+C!')
        log.warning('Leaving now. Bye!\n')
        pass

    return


def pickable_file_to_database(args):
    print(args)
    # file_to_database(args['file'], args['keys'], args['cursor'])


if __name__ == '__main__':

    # Parsing Arguments ---
    parser = argparse.ArgumentParser(
        description="Reduce SAMI's or SAM-FP data."
    )

    parser.add_argument(
        '-D', '--debug', action='store_true',
        help="Turn on DEBUG mode (overwrite quiet mode)."
    )
    parser.add_argument(
        '-q', '--quiet', action='store_true',
        help="Run quietly."
    )
    parser.add_argument(
        '--database', default=None,
        help='Data-base name (in case you do not want the default name).'
    )
    parser.add_argument(
        'root_dir', type=str,
        help="Root directory."
    )

    args = parser.parse_args()

    if not args.quiet:
        log.setLevel(logging.INFO)

    if args.debug:
        log.setLevel(logging.DEBUG)

    log.info('\n Create Database\n  by Bruno C. Quint')
    log.debug('\n\n Current log level: %s' % log.level)

    root_dir = args.root_dir
    root_dir = os.path.abspath(root_dir)
    log.info(' Walking through %s folder' % root_dir)

    database_filename = os.path.join(root_dir, 'temp.db') \
        if args.database is None else os.path.join(root_dir, args.database)
    msg = 'Loading' if os.path.exists(database_filename) else 'Creating'
    log.info(' %s database: %s' % (msg, database_filename))
    con = lite.connect(database_filename)
    cur = con.cursor()

    keys = {
        '"DATE-OBS"': 'TEXT',
        '"TIME-OBS"': 'TEXT',
        'NEXTEND': 'INTEGER',
        'OBSTYPE': 'TEXT',
        'OBJECT': 'TEXT',
        'RA': 'TEXT',
        'DEC': 'TEXT',
        'EXPTIME': 'REAL',
        'FILTER1': 'TEXT',
        'FAPERSID': 'TEXT',
        'FAPERSWP': 'TEXT',
        'FAPERSST': 'TEXT',
        'FAPEROTZ': 'INTEGER'
    }

    s = 'CREATE TABLE IF NOT EXISTS my_table('
    for key in keys:
        s += '%s %s, ' % (key, keys[key])
    s = s[:-2] + ');'
    s.replace('""', '"')
    cur.execute(s)

    # fix_headers(root_dir)
    files_to_database(root_dir, keys, con)

    cur.execute('SELECT * FROM my_table;')

    if con:
        con.close()
