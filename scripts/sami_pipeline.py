#!/usr/bin/env python 
# -*- coding: utf8 -*-

from __future__ import division, print_function

import os

__author__ = 'Bruno Quint'

if __name__ == '__main__':

    # Path on soarbr3
    path = "/home/bquint/Data/SAMFP/20170402"

    # Walk over files
    for root, dirs, files in os.walk(path):

        
