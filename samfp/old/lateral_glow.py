#!/usr/bin/env python
# -*- coding: utf8 -*-

import astropy.io.fits as pyfits
import numpy as np
import matplotlib.pyplot as plt
import cv2

from matplotlib import gridspec

filename = '/home/bquint/Data/SAM/Lateral_Glowing/DARK180s.fits'
data = pyfits.getdata(filename=filename)
print(data.mean())
print(np.median(data))

# gs = gridspec.GridSpec(2, 2, width_ratios=[1, 9], height_ratios=[9, 1])
#
# ax1 = plt.subplot(gs[0, 1])
# ax1.imshow(data, origin='lower', interpolation='nearest', cmap='cubehelix')
# ax1.set_xticklabels([])
# ax1.set_yticklabels([])
# ax1.set_xlim(0, data.shape[0])
# ax1.set_ylim(0, data.shape[1])
#
# x = data.sum(axis=1)
# y = np.arange(x.size)
# ax2 = plt.subplot(gs[0, 0], sharey=ax1)
# ax2.plot(x, y, 'k-')
# ax2.set_ylim(0, y.size)
#
# y = data.sum(axis=0)
# x = np.arange(y.size)
# ax3 = plt.subplot(gs[1, 1], sharex=ax1)
# ax3.plot(x, y, 'k-')
# ax3.set_xlim(0, x.size)
#
# plt.show()

img = cv2.medianBlur(data, 5)
print((img == np.nan).any())
print((img == -np.infty).any())
print((img == +np.infty).any())

print(img.__class__)
print(np.min(img))
print(np.max(img))
print(np.mean(img))
print(np.median(img))

plt.imshow(img, 'gray')
plt.show()

