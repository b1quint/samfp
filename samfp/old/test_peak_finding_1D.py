#!/usr/bin/env python 
# -*- coding: utf8 -*-
"""
This script was created to test different algorithms for peak finding in
different situations.

    by Bruno Quint
"""
import numpy as np
import matplotlib.pyplot as plt

from astropy.modeling import fitting, models
from scipy import signal

__author__ = 'Bruno Quint'

if __name__ == '__main__':

    snr = 5.0
    window_size = 0.25 # % of the total width

    fig = plt.figure(1)
    gs = plt.GridSpec(2, 1, height_ratios=[5, 1])
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1], sharex=ax1)

    x = np.linspace(0, 10, 1000)

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
    y = g(x) + n

    l1, = ax1.plot(x, y, 'k-')
    l2, = ax1.plot(x, g(x), 'r-', lw=2)
    ax1.set_ylabel('Y [--]')
    ax1.set_title('1D Peak Detection')
    ax1.grid()
    plt.setp(ax1.get_xticklabels(), visible=False)

    peaks = signal.argrelmax(y, order=int(window_size * x.size), axis=0)[0]

    for p in peaks:
        ax1.axvline(x[p], c='k', ls='--')
        print("y[{}] = {}".format(x[p], y[p]))

    ax1.axvline(g1.mean, c='r', ls='--')
    ax1.axvline(g2.mean, c='r', ls='--')

    l3, = ax2.plot(x, y - g(x), 'kx')
    ax2.set_ylabel('y - g(x)')
    ax2.set_ylim(-1, 1)
    ax2.set_yticks([-1, 0, 1])
    ax2.grid()

    leg = fig.legend([l1, l2, l3], ['Noisy data', 'Original Data', 'Residual'],
                     mode='expand', loc='lower center', ncol=3)

    # TODO find legend's height and use it in the argument bellow
    fig.tight_layout(rect=[0, 0.1, 1, 1])
    plt.show()

