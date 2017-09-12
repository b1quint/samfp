"""
    0.0.0 - Starting from old version. Some features may not be working. My
            idea is to implement each of the scripts as a bin to be installed
            using setup.py and the entry_points keyword.
    0.1.0 - xjoin was released again. It is working and installed using
            entry_points.
    0.2.0 - mkcube can now be called as script again and it is installed using
            pip.
    0.3.0 - phmxtractor can now be called as script again and it is installed
            using pip.
    0.4.0 - phmfit can now be called as script again and it is installed using
            pip.
    0.4.1 - phmfit now stores fit parameters in the header.
    0.5.0 - phmapply back to work.

    0.6.0 - Add tools to combine Bias, Flats, Darks and Images.
       .1 - Fixed some installation issues.
"""

api = 0
feature = 6
bug = 1

month = 8
year = 2017

__str__ = '{:d}.{:d}.{:d} {:d}-{:d}'.format(api, feature, bug, month, year)
