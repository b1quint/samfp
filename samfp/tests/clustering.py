#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
import numpy as np

from matplotlib import gridspec
from scipy import signal


class Parabola:

    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def __call__(self, x):
        y = self.a * x ** 2 + self.b * x + self.c
        return y


# Use Kernel Density Estimation to identify the two different clusters
def kde_scipy(x, x_grid, bandwidth=0.2, **kwargs):
    """Kernel Density Estimation with Scipy"""
    # Note that scipy weights its bandwidth by the covariance of the
    # input data.  To make the results comparable to the other methods,
    # we divide the bandwidth by the sample standard deviation here.
    kde = stats.gaussian_kde(x, bw_method=bandwidth / x.std(ddof=1),
                             **kwargs)
    return kde.evaluate(x_grid)


# Create my initial parabola
fsr = 60
x = np.linspace(0, 10, 100)
p = Parabola(1, -10, 10)
y = p(x) + (np.random.random_sample(x.size) - 0.5) * 1

# Add a fake shift representing the fsr
y[y < 0] += fsr

# Add a second FSR
y = np.concatenate((y, y + fsr))
x = np.concatenate((x, x))

# Plot this
fig = plt.figure()

gs = gridspec.GridSpec(2, 1)
ax1 = fig.add_subplot(gs[0])
ax1.plot(y, x, 'k+')
ax1.set_xlabel("y")
ax1.set_ylabel("x")

# Create a lateral plot to visualize the distribution in 1D since I do not
# care about the 2D distribution.
x_ = -2 * np.ones_like(x) + np.random.random_sample(x.size) * 0.1

ax1.plot(y, x_, 'kx', alpha=0.10)

# Make a histogram
bins = np.linspace(y.min(), y.max(), 50)

ax2 = fig.add_subplot(gs[1])
ax2.hist(y, bins=bins, alpha=0.5)

# Split
y_indexes = np.argsort(y)
y_ = np.sort(y)
yl_ = np.diff(y_)
ayl_ = np.abs(yl_)
ayl_[np.abs(ayl_ - np.median(ayl_)) < np.std(ayl_)] = 0
split_indexes = signal.argrelmax(ayl_)[0]

split_y_indexes = np.split(y_indexes, split_indexes + 1)

for (i, idx) in enumerate(split_y_indexes):
    ax1.plot(y[idx], x[idx], 'o', alpha=0.25)
    y[idx] -= fsr * i
    ax1.plot(y[idx], x[idx], 'ko', alpha=0.10)

# Display the plot
plt.tight_layout()
plt.show()