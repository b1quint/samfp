#/usr/bin/env python

from distutils.core import setup

setup(
    name='samfp',
    version='0.1.1',
    description='SAM-FP Data Reduction Pipeline',
    url='https://github.com/b1quint/samfp',
    author='Bruno Quint',
    author_email='bquint@ctio.noao.edu',
    license='3-clause BSD License',
    packages=['samfp'],
    package_dir={'samfp': 'samfp'},
    # package_data={},
    scripts=['scripts/xjoin'],
    zip_safe=False,
)