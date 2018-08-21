#!/usr/bin/env python 
# -*- coding: utf8 -*-
"""


"""
from __future__ import division, print_function

import os
import sys

from .logger import get_logger

__author__ = 'Bruno Quint'


def safe_save(name, extension=None, overwrite=False, verbose=False):
    """
        This is a generic method used to check if a file called 'name'
        already exists. If so, it starts some interaction with the user.

        Parameters:
            name : str
                The name of the file that will be written in the future.

            extension: str (default=None)
                Check if the file has the following extension. If not, it fills
                for the user. Defaults is None. An example would be
                extension='.fits'.

            overwrite : bool
                If False, this method will interact with the user to ask if 'name'
                file shall be overwritten or if a new name will be given. If True,
                'name' file is automatically overwritten.

            verbose : bool
                force verbose mode on even when overwrite is automatic.
    """
    _log = get_logger(__name__)

    if verbose:
        _log.setLevel('INFO')

    if os.path.splitext(name)[1] != extension and extension is not None:
        name = name + extension

    _log.info('Writing to output file "%s"' % name)

    while os.path.exists(name):

        if overwrite in ['y', 'Y', True]:
            _log.info("Overwriting %s file." % name)
            os.remove(name)

        elif overwrite in ['', 'n', 'N', False]:
            name = input("    Please, enter a new filename:\n    > ")
            if os.path.splitext(name)[1] != extension and extension is not None:
                name = name + extension

        elif overwrite in ['q']:
            _log.info("Exiting program.")
            sys.exit()

        else:
            overwrite = input(" '%s' file exist. Overwrite? (y/[n])" % name)
            _log.info('Writing to output file "%s"' % name)

    return name