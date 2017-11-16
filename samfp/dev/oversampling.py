#!/usr/bin/env python

from scipy import interpolate
from pylab import *
import matplotlib.pyplot as plt

def gaussian(x, mu, sig):
    return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))

ncan = 36

x = np.arange(ncan)+1
print('x.size=',x.size,x)

mu= 13
sig = 3
g = 100*gaussian(x, mu, sig)
g = np.zeros(ncan)
g[12] = 200.
print('g.size=',g.size,g)
gsum = np.sum(g)
print('g=',gsum)

x5 = np.hstack((x - 2*ncan,x - ncan, x, x + ncan, x + 2*ncan))
print('x5.size=',x5.size,x5)
g5 = gaussian(x5, 0., 1e-20)
g5 = np.zeros(5*ncan)
for i in range(-2,3,1):
    g5[12+i*ncan] = 200.
g5sum = np.sum(g5)
print('g5=',g5sum)
#for i in range(-2,3,1):
#    g5 = g5 + 100*gaussian(x5, mu-i*ncan, sig)
print('g5.size=',g5.size,g5)
#f = interpolate.interp1d(x5, g5,kind='cubic')
f = interpolate.interp1d(x5, g5,kind='linear')

overs = 3
x3 = np.hstack((x - ncan, x, x + ncan))
print('x3.size=',x3.size,x3)

x33 = np.linspace(x3.min(), x3.max()+(overs-1)/overs, overs * x3.size)
g33 = f(x33)/overs
print('x33.size=',x33.size,x33)
print('g33.size=',g33.size,g33)
g33sum = np.sum(g33)
print('g33sum=',g33sum)

y = x33[ncan*overs:-ncan*overs]
g3 = g33[ncan*overs:-ncan*overs]
print('y.size=',y.size,y)
print('g3.size=',g3.size,g3)
g3sum = np.sum(g3)
print('g3sum=',g3sum)

plt.tick_params(axis='both',which='both',direction='in',top='on',right='on')
plt.xlabel("Channel", fontsize=10)
plt.ylabel("Flux", fontsize=10)

plt.plot(x5,g5,c='yellow',marker='.',linestyle='None')
plt.plot(x33,g33,c='blue',marker='x',linestyle='None')
plt.plot(y,g3,c='red',marker='s',linestyle='None')
plt.plot(x,g,c='black',marker='v',linestyle='None')

xmin, xmax = xlim()
ymin, ymax = ylim()
plt.xlim(xmin, xmax)
plt.ylim(ymin, ymax)

plt.show()
#plt.savefig('interpolate'+'.pdf')