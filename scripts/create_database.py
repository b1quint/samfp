#!/usr/bin/env python2
"""
    Reduce Everything

    This script was created with the intention to reduce all SAMI's data. For
    now, here is it's current features:


    by Bruno C. Quint
"""

from __future__ import print_function, division

import argparse
import logging
import os
import sqlite3

from ccdproc import ImageFileCollection

# Setting log
logging.captureWarnings(False)
log_fmt = logging.Formatter()
log_handler = logging.StreamHandler()
log_handler.setFormatter(log_fmt)
log = logging.getLogger(__name__)
log.addHandler(log_handler)
log.setLevel(logging.NOTSET)


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
        '--database',
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

    root_dir = args.root_dir
    root_dir = os.path.abspath(root_dir)

    keys = ['obstype', 'object','RA', 'DEC', 'EXPTIME']
    ic = ImageFileCollection(root_dir, keywords=keys)
    df = ic.summary.to_pandas()




