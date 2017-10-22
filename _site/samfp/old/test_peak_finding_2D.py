#!/usr/bin/env python 
# -*- coding: utf8 -*-
"""
This script was created to test different algorithms for peak finding in
different situations.

    by Bruno Quint
"""
import itertools
import numpy as np
import matplotlib.pyplot as plt

from astropy.modeling import fitting, models
from scipy import signal

__author__ = 'Bruno Quint'


if __name__ == '__main__':

    snr = 50.0
    window_size = 0.25 # % of the total width
    nx = 100
    ny = 100

    fig = plt.figure(1)
    gs = plt.GridSpec(1, 1)
    ax1 = fig.add_subplot(gs[0])

    x = np.linspace(0, 10, nx)
    x = np.reshape(x, (1, x.size))
    x = np.repeat(x, 100, axis=0)

    g1 = models.Gaussian1D()
    g1.amplitude = 1.
    g1.mean = 3.5
    g1.stddev = 1

    g2 = models.Gaussian1D()
    g2.amplitude = 1.
    g2.mean = 6.5
    g2.stddev = 1

    g = g1 + g2

    n = np.random.normal(loc=0.0, scale=g1.amplitude / snr, size=x.size)
    n = np.reshape(n, x.shape)
    y = g(x) + n

    ax1.imshow(y, origin='lower', cmap='gray_r', interpolation='nearest')
    ax1.set_xticklabels([])
    ax1.set_yticklabels([])
    ax1.axvline(g1.mean * (nx / x.ptp()), c='red', lw=2)
    ax1.axvline(g2.mean * (nx / x.ptp()), c='red', lw=2)

    wsize = int(window_size * nx)
    find_peak = lambda i: signal.argrelmax(y[i], axis=0, order=wsize)[0]

    peaks = map(find_peak, np.arange(ny))
    peaks = np.array(peaks)
    p = np.zeros((nx, ny, 4))
    for (i, j) in zip(range(ny), peaks):
        p[i, j, 0] = 1
        p[i, j, 3] = 0.7

    ax1.imshow(p, origin='lower', interpolation='nearest')

    ax1.set(title='2D Peak Finding')
    fig.tight_layout(rect=[0, 0, 1, 1])
    plt.show()

