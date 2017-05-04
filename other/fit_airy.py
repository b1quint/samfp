#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from fptools.fpreduc import pyadhoc
import ipdb
import time
import pyfits as pf

#from mpfit import mpfit
import mpyfit
from scipy.optimize import curve_fit
#import lmfit


def gaussian_mpyfit(x, p):
    return p[0] + p[1] * np.exp( -0.5 * (x - p[2]) ** 2 / (2 * p[3] ** 2))

def least_mpyfit(p, args):
    #t1 = time.time()
    I0, C, F, ne, b, xc, yc = p
    lbda, x, y, data, flat = args
    res = (airy2d(I0=I0, C=C, F=F, ne=ne, b=b, xc=xc, yc=yc, lbda=lbda, x=x, y=y) - data) * flat
    #t2 = time.time()
    #print(t2 - t1)
    return(res.flatten())

def airy2d(I0=1., C=0., F=15., ne=250., b=9.e-6, xc=256., yc=256., lbda=0.6563, x=512, y=512):
    
    '''
    Airy function in order to compute a ring
    
    Parameters
    ----------
    
    I0: float
        intensity,
    C: float
        intensity,
    F: float
        finesse,
    ne: float
        optical thickness between the two FP plates (micron),
    b: float
        ratio of the pixel size over the camera focal lenght,
    xc: float
        ring center x coordinate,
    yc: float
        ring center y coordinate,
    lbda: float
        wavelength (micron), 
    x: integer
        x-size of the image, 
    y: integer
        y-size of the image.
        
    Return
    ------
    
    out : ndarray
        An image of a ring with the above parameters given as input
    '''

    # we need the indices of the pixels in image
    index = np.indices((y, x))
    # radius in pixel with respect to the ring center (optical axis)
    rpix = np.sqrt((index[1] - xc) ** 2 + (index[0] - yc) ** 2)
    # incidnence angle in radians
    #theta = np.arctan(b * rpix)
    # function of Airy I
    f = 4.0 * F ** 2 / np.pi ** 2
    #phi = 4.0 * np.pi * ne * np.cos(theta) / lbda
    phi2 = 2.0 * np.pi * ne / (lbda * np.sqrt(1 + b ** 2 * rpix ** 2))
    I = C + I0 / ( 1. + f * np.sin(phi2) ** 2 )

    return I


def airy2d0(I0=1., C=0., F=15., ne=250., b=9.e-6, xc=256., yc=256., lbda=0.6563, index=None):
    
    '''
    Airy function in order to compute a ring
    
    Parameters
    ----------
    
    I0: float
        intensity,
    C: float
        intensity,
    F: float
        finesse,
    ne: float
        optical thickness between the two FP plates (micron),
    b: float
        ratio of the pixel size over the camera focal lenght,
    xc: float
        ring center x coordinate,
    yc: float
        ring center y coordinate,
    lbda: float
        wavelength (micron), 
    x: integer
        x-size of the image, 
    y: integer
        y-size of the image.
        
    Return
    ------
    
    out : ndarray
        An image of a ring with the above parameters given as input
    '''

    # radius in pixel with respect to the ring center (optical axis)
    rpix = np.sqrt((index[1] - xc) ** 2 + (index[0] - yc) ** 2)
    # incidnence angle in radians
    #theta = np.arctan(b * rpix)
    # function of Airy I
    f = 4.0 * F ** 2 / np.pi ** 2
    #phi = 4.0 * np.pi * ne * np.cos(theta) / lbda
    phi2 = 2.0 * np.pi * ne / (lbda * np.sqrt(1 + b ** 2 * rpix ** 2))
    I = C + I0 / ( 1. + f * np.sin(phi2) ** 2 )

    return I

def main():
    
    ##################
    # Model as input #
    ##################
    
    # Parameter initialisation for the model (obtained from the data)
    lbda = 0.6598
    pc = 791
    r1 = (347. - 142.) / 2.
    r2 = (456. - 33) / 2.
    b = np.sqrt((2 * pc - 1) / (pc **2 * (r2 ** 2 - r1 ** 2) - 2 * pc * r2 ** 2 + r2 ** 2))
    ne = lbda * pc * np.sqrt(1 + b ** 2 * r1 ** 2) / 2.
    isl_ne = ne / pc
    de = - isl_ne / 33.
    
    x, y, = 512, 512
    image = np.zeros((y, x))
    index = np.indices((y, x))
    
    I0, C, F, xc, yc = 2000., 300., 11.7, 244.1, 239.9
    
    print(I0, C, F, ne, b, xc, yc)
    
    cube = np.zeros((32, y, x))
    for z in range(32):
        data = airy2d(I0=I0, C=C, F=F, ne=ne-z*de, b=b, xc=xc, yc=yc, lbda=lbda, x=x, y=y)
        cube[z, :,:] = data.reshape((1, y, x))
    hdu = pf.PrimaryHDU(cube)
    hdulist = pf.HDUList(hdu)
    hdulist.writeto('/home/bepinat/Travail/mission_ohp_1014/test/T251/model.fits', clobber=True)
    
    
    
    data = airy2d(I0=I0, C=C, F=F, ne=ne, b=b, xc=xc, yc=yc, lbda=lbda, x=x, y=y)
    #data = airy2d0(I0=I0, C=C, F=F, ne=ne, b=b, xc=xc, yc=yc, lbda=lbda, index=index)
    
    #Initial data plot
    fig = plt.figure()
    ax1 = plt.subplot(131)
    plt.imshow(data, vmin=290, vmax=2500, cmap='spectral')
    plt.colorbar(orientation="horizontal")

    # Parameter initialisation
    f = 4.0 * F ** 2 / np.pi ** 2
    I0 = (np.percentile(data, 99) - np.percentile(data, 1)) * (1 + f) / f
    C = np.percentile(data, 99) - I0
    F = 13.
    b = 2.72e-04
    ne = ne + lbda / 16.
    xc = xc + 10.5
    yc = yc - 5.2
    flat = 1
    pi = (I0, C, F, ne, b, xc, yc)
    print(pi)
    
    # Constraints on parameters
    #parbase = {'fixed':1, 'limits':(None, None), 'step':0.1, 'relstep':0.1, 'side':0, 'deriv_reltol':1e-6, 'deriv_abstol':1e-6}
    parinfo = []
    parbase = {'fixed':False, 'limits':(I0 * 0.9, I0 * 1.1)}
    parinfo.append(parbase)
    parbase = {'fixed':False, 'limits':(C * 0.9, C * 1.1)}
    parinfo.append(parbase)
    parbase = {'fixed':False, 'limits':(F / 1.5, F * 1.5)}
    parinfo.append(parbase)
    parbase = {'fixed':False, 'limits':(ne - lbda / 4., ne + lbda / 4.)}
    parinfo.append(parbase)
    parbase = {'fixed':False, 'limits':(b * 0.96, b * 1.04)}
    parinfo.append(parbase)
    parbase = {'fixed':False, 'limits':(xc - 15, xc + 15)}
    parinfo.append(parbase)
    parbase = {'fixed':False, 'limits':(yc - 15, yc + 15)}
    parinfo.append(parbase)
    
    # Fit
    pfit, results = mpyfit.fit(least_mpyfit, pi, args=(lbda, x, y, data, flat), parinfo=parinfo, stepfactor=10)
    print(pfit, results['bestnorm'])
    
    # Model
    result = airy2d(I0=pfit[0], C=pfit[1], F=pfit[2], ne=pfit[3], b=pfit[4], xc=pfit[5], yc=pfit[6], lbda=lbda, x=x, y=y)
    
    # Residualks and plot of residuals
    residuals = data - result
    ax1 = plt.subplot(133)
    plt.imshow(residuals, vmin=-.02, vmax=.02, cmap='spectral')
    plt.colorbar(orientation="horizontal")
    plt.show()
    
    
    #################
    # Data as input #
    #################
    
    tdu = pyadhoc.readad3('/home/bepinat/Travail/mission_ohp_1014/test/T251/T251.AD3')
    index = 0
    
    # Initial data plot
    fig = plt.figure()
    ax1 = plt.subplot(141)
    plt.imshow(tdu.data[index,:,:].reshape((512,512)), vmin=290, vmax=2500, cmap='spectral')
    plt.colorbar(orientation="horizontal")

    # Construction of a flat field for calibration (relie on the hypothesis that the free spectral range is correctly sampled)
    bkg = np.percentile(tdu.data, 0.1)  # background
    flat = np.sum((tdu.data - bkg), axis=0)  # background substraction
    flat[np.where(flat <= 0)] = 1  # remove zeros
    flat /= np.percentile(flat, 99)  # normalization
    ax1 = plt.subplot(142)
    #flat = 1
    plt.imshow(flat, vmin=0, vmax=1, cmap='spectral')
    plt.colorbar(orientation="horizontal")

    data = (tdu.data[index,:,:].reshape((512,512)) - bkg) / flat + bkg  # flat field correction
    data[np.where(data < 300)] = 300
    data[np.where(data > 3000)] = 300
    
    datahdu = (tdu.data - bkg) / flat + bkg
    datahdu[np.where(datahdu < 300)] = 300
    datahdu[np.where(datahdu > 3000)] = 300
    hdu = pf.PrimaryHDU(datahdu)
    hdulist = pf.HDUList(hdu)
    hdulist.writeto('/home/bepinat/Travail/mission_ohp_1014/test/T251/T251_norm.fits', clobber=True)

    # Flat fielded data plot
    ax1 = plt.subplot(143)
    plt.imshow(data, vmin=290, vmax=2500, cmap='spectral')
    plt.colorbar(orientation="horizontal")
    plt.show()
    
    # Parameter initialisation
    lbda = 0.6598
    pc = 791
    r1 = (347. - 142.) / 2.
    r2 = (456. - 33) / 2.
    b = np.sqrt((2 * pc - 1) / (pc **2 * (r2 ** 2 - r1 ** 2) - 2 * pc * r2 ** 2 + r2 ** 2))
    ne = lbda * pc * np.sqrt(1 + b ** 2 * r1 ** 2) / 2.
    
    f = 4.0 * F ** 2 / np.pi ** 2
    I0 = (np.percentile(data, 99) - np.percentile(data, 1)) * (1 + f) / f
    C = np.percentile(data, 99) - I0
    pi = (I0, C, F, ne, b, xc, yc)
    print(pi)
    
    # Constraints on parameters
    #parbase = {'fixed':1, 'limits':(None, None), 'step':0.1, 'relstep':0.1, 'side':0, 'deriv_reltol':1e-6, 'deriv_abstol':1e-6}
    parinfo = []
    parbase = {'fixed':False, 'limits':(I0 * 0.9, I0 * 1.1)}
    parinfo.append(parbase)
    parbase = {'fixed':False, 'limits':(C * 0.9, C * 1.1)}
    parinfo.append(parbase)
    parbase = {'fixed':False, 'limits':(F / 1.5, F * 1.5)}
    parinfo.append(parbase)
    parbase = {'fixed':False, 'limits':(ne - lbda / 4., ne + lbda / 4.)}
    parinfo.append(parbase)
    parbase = {'fixed':False, 'limits':(b * 0.96, b * 1.04)}
    parinfo.append(parbase)
    parbase = {'fixed':False, 'limits':(xc - 15, xc + 15)}
    parinfo.append(parbase)
    parbase = {'fixed':False, 'limits':(yc - 15, yc + 15)}
    parinfo.append(parbase)
    
    # Fit
    pfit, results = mpyfit.fit(least_mpyfit, pi, args=(lbda, x, y, data, flat), parinfo=parinfo, stepfactor=10)
    print(pfit, results['bestnorm'])
    
    # Model
    result = airy2d(I0=pfit[0], C=pfit[1], F=pfit[2], ne=pfit[3], b=pfit[4], xc=pfit[5], yc=pfit[6], lbda=lbda, x=x, y=y)
    
    # Residuals and plot of residuals
    residuals = data - result
    ax1 = plt.subplot(144)
    plt.imshow(residuals, vmin=-250, vmax=250, cmap='spectral')
    plt.colorbar(orientation="horizontal")
    plt.show()
    

    ##Several planes
    #II = []
    #CC = []
    #FF = []
    #nnee = []
    #bb = []
    #xxc = []
    #yyc = []
    #for index in np.arange(0, tdu.data.shape[0], 6):
        #fig = plt.figure()
        #ax1 = plt.subplot(131)
        #plt.imshow(tdu.data[index,:,:].reshape((512,512)), vmin=290, vmax=2500, cmap='spectral')
        #plt.colorbar(orientation="horizontal")
    
        #bkg = np.percentile(tdu.data, 0.1)
        #flat = np.sum((tdu.data - bkg), axis=0)
        #flat[np.where(flat <= 0)] = 1
        #flat /= np.percentile(flat, 99)
    
        #data = (tdu.data[index,:,:].reshape((512,512)) - bkg) / flat + bkg
        #ax1 = plt.subplot(132)
        #plt.imshow(data, vmin=290, vmax=2500, cmap='spectral')
        #plt.colorbar(orientation="horizontal")
        #plt.show()
        
        
        #print(I0, C, F, ne, b, xc, yc)
        #f = 4.0 * F ** 2 / np.pi ** 2
        #I0 = (np.percentile(data, 99) - np.percentile(data, 1)) * (1 + f) / f
        #C = np.percentile(data, 99) - I0
        ##F=13.
        ##b=2.e-4
        ##ne = lbda * pc / 2. + lbda / 8. - lbda / 16.
        ##pi = (I0, C, F, ne, b, xc + 10.5, yc - 10.2)
        ##flat = 1
        ###pi = (I0, ne - lbda / 8., xc, yc)
        
        #pi = (I0, C, F, ne, b, xc, yc)
        #print(pi)
        ##parbase = {'fixed':1, 'limits':(None, None), 'step':0.1, 'relstep':0.1, 'side':0, 'deriv_reltol':1e-6, 'deriv_abstol':1e-6}
        #parinfo = []
        #parbase = {'fixed':False, 'limits':(I0 * 0.9, I0 * 1.1)}
        #parinfo.append(parbase)
        #parbase = {'fixed':True, 'limits':(C * 0.9, C * 1.1)}
        #parinfo.append(parbase)
        #parbase = {'fixed':True, 'limits':(F / 1.5, F * 1.5)}
        #parinfo.append(parbase)
        #parbase = {'fixed':False, 'limits':(ne - lbda / 4., ne + lbda / 4.)}
        #parinfo.append(parbase)
        #parbase = {'fixed':True, 'limits':(b * 0.96, b * 1.04)}
        #parinfo.append(parbase)
        #parbase = {'fixed':False, 'limits':(xc - 10, xc + 10)}
        #parinfo.append(parbase)
        #parbase = {'fixed':False, 'limits':(yc - 10, yc + 10)}
        #parinfo.append(parbase)
        ##parinfo
        #pfit, results = mpyfit.fit(least_mpyfit, pi, args=(lbda, x, y, data, flat), parinfo=parinfo, stepfactor=10)
        #print(pfit, results['bestnorm'])
        
        #result = airy2d(I0=pfit[0], C=pfit[1], F=pfit[2], ne=pfit[3], b=pfit[4], xc=pfit[5], yc=pfit[6], lbda=lbda, x=x, y=y)
        
        #residu = data - result
        #ax1 = plt.subplot(133)
        #plt.imshow(residu, vmin=-500, vmax=500, cmap='spectral')
        #plt.colorbar(orientation="horizontal")
        #plt.show()
        #II.append(pfit[0])
        #CC.append(pfit[1])
        #FF.append(pfit[2])
        #nnee.append(pfit[3])
        #bb.append(pfit[4])
        #xxc.append(pfit[5])
        #yyc.append(pfit[6])
        #ne = pfit[3]
    
    ##ca ajuste si on fixe la finesse (peut varier entre +- 50%), le centre dans un rayon ~20 pixels, le continu, l'épaisseur dans +- lbda/4 et le param b
    ##En principe, si arrive a determiner b relativement précisement (àa mieux que +-4%) et ne (a partir de 2 anneaux), ca devrait ajuster

    ##J'aimerais tester avec plusieurs ordres pour voir si on arrive a partir du chi2 a determiner l'ordre: non car compensé par la focale!
    ##Si la focale est fixee, ca converge bien vers l'ordre pc (mais il faut que la finesse soit libre)
    #index = 0
    #bkg = np.percentile(tdu.data, 0.1)
    #flat = np.sum((tdu.data - bkg), axis=0)
    #flat[np.where(flat <= 0)] = 1
    #flat /= np.percentile(flat, 99)
    #data = (tdu.data[index,:,:].reshape((512,512)) - bkg) / flat + bkg
    #opc = 791
    #bn = []
    #for pc in np.arange(opc - 4, opc + 5):
        ##b = np.sqrt((2 * pc - 1) / (pc **2 * (r2 ** 2 - r1 ** 2) - 2 * pc * r2 ** 2 + r2 ** 2))
        #ne = lbda * pc * np.sqrt(1 + b ** 2 * r1 ** 2) / 2.
                
        #f = 4.0 * F ** 2 / np.pi ** 2
        #I0 = (np.percentile(data, 99) - np.percentile(data, 1)) * (1 + f) / f
        #C = np.percentile(data, 99) - I0
        #pi = (I0, C, F, ne, b, xc, yc)
        #print(pi)

        #parinfo = []
        #parbase = {'fixed':False, 'limits':(I0 * 0.9, I0 * 1.1)}
        #parinfo.append(parbase)
        #parbase = {'fixed':False, 'limits':(C * 0.9, C * 1.1)}
        #parinfo.append(parbase)
        #parbase = {'fixed':False, 'limits':(F / 1.5, F * 1.5)}
        #parinfo.append(parbase)
        #parbase = {'fixed':False, 'limits':(ne - lbda / 4., ne + lbda / 4.)}
        #parinfo.append(parbase)
        #parbase = {'fixed':True, 'limits':(b * 0.96, b * 1.04)}
        #parinfo.append(parbase)
        #parbase = {'fixed':False, 'limits':(xc - 10, xc + 10)}
        #parinfo.append(parbase)
        #parbase = {'fixed':False, 'limits':(yc - 10, yc + 10)}
        #parinfo.append(parbase)
        ##parinfo
        #pfit, results = mpyfit.fit(least_mpyfit, pi, args=(lbda, x, y, data, flat), parinfo=parinfo, stepfactor=10)
        #print(pfit)
        #bn.append(results['bestnorm'])
        #result = airy2d(I0=pfit[0], C=pfit[1], F=pfit[2], ne=pfit[3], b=pfit[4], xc=pfit[5], yc=pfit[6], lbda=lbda, x=x, y=y)
        
        ##residu = data - result
        ##fig = plt.figure()
        ##plt.imshow(residu, vmin=-500, vmax=500, cmap='spectral')
        ##plt.colorbar(orientation="horizontal")
        ##plt.show()
        #print(pc, pfit[2], results['bestnorm'])
    #q = np.array(bn)
    #ind = np.where(q == np.min(q))
    #orders = np.arange(opc - 4, opc + 5)
    #print(q[ind], orders[ind])


if __name__ == "__main__":
    main()
    