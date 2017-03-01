#!/usr/bin/env python 
# -*- coding: utf8 -*-

import numpy as np
from scipy import signal

x = np.array([2, 1, 2, 3, 2, 0, 1, 0])
print(x)

peaks = signal.argrelmax(x)
print(peaks)
for p in peaks:
    print("x[{}] = {}".format(p, x[p]))

print('\n---')
y = np.array([[2, 1, 2, 3, 2, 0, 1, 0],
              [2, 1, 2, 2, 3, 0, 1, 0]])
peaks = signal.argrelmax(y, axis=1)[0]
for p in peaks:
    print("y[{}] = {}".format(p, y[p]))



