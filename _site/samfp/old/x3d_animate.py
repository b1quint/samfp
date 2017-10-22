#!/usr/bin/env python 
# -*- coding: utf8 -*-

from __future__ import division, print_function

import matplotlib as mpl
mpl.use('Agg')
mpl.rcParams['image.origin'] = 'lower'
mpl.rcParams['image.interpolation'] = 'nearest'
mpl.rcParams['image.cmap'] = 'gray_r'

from scipy import ndimage
from matplotlib import animation

import astropy.io.fits as pyfits
import matplotlib.pyplot as plt
import astropy.visualization as viz
import numpy as np
import os

__author__ = 'Bruno Quint'

def main():

    # Input Data ---
    path = "/home/bquint/Dropbox/temp/30Dor_NII/"
    filename = "30DorNII_3D_WCL.fits"

    # Create/Read Cube ---
    cube = DataCube(os.path.join(path, filename))
    print(cube)

    # Create figure to animate ---
    fig = plt.figure(figsize=(5,5), frameon=False)
    ax = fig.add_axes([0,0,1,1])
    ax.axis('off')

    n1 = viz.ImageNormalize(cube.get_frame(0), interval=viz.ZScaleInterval())
    n2 = viz.ImageNormalize(cube.get_frame(20), interval=viz.ZScaleInterval())

    im = ax.imshow(cube.get_frame(0), animated=True, vmin=n1.vmin, vmax=n2.vmax)

    def update(i):
        im.set_array(cube.get_frame(i))
        return im,

    ani = animation.FuncAnimation(fig, update, interval=100, repeat=True, frames=cube.depth)
    ani.save(cube.filename.replace('.fits', '.gif'), writer="imagemagick", fps=30)
    plt.show()


class DataCube(object):

    def __init__(self, filename):

        cube = pyfits.getdata(filename)

        self.min = cube.min()
        self.max = cube.max()
        self.mean = cube.mean()
        self.std = cube.std()
        self.median = np.median(cube)
        self.filename = filename
        self.depth, self.heigh, self.width = cube.shape

        del cube
        return

    def __str__(self):
        s = (
            "Cube Description: \n"
            " Min = {min:.2f}\n"
            " Max = {max:.2f}\n"
            " Mean = {mean:.2f}\n"
            " Median = {median:.2f}\n"
            " STD = {std:.2f}\n"
        ).format(**self.__dict__)
        return s

    def get_frame(self, i):
        temp = pyfits.getdata(self.filename)[i]
        temp = ndimage.median_filter(temp, 3)
        return temp

    def get_cube(self):
        return pyfits.getdata(self.filename)

    def get_max_frame(self):
        temp = pyfits.getdata(self.filename)
        temp = np.sum(temp, axis=2)
        temp = np.sum(temp, axis=1)
        temp = np.argmax(temp)
        return temp

if __name__ == '__main__':
    main()
