#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from scipy import ndimage
import cv2
import matplotlib as mpl
import matplotlib.pyplot as plt
from fptools.fpreduc import pyadhoc
import copy
import ipdb

#from mpfit import mpfit
import mpyfit
#from scipy.optimize import curve_fit
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

    image = np.zeros((y, x))
    # we need the indices of the pixels in image
    ind = np.indices((y, x))
    # radius in pixel with respect to the ring center (optical axis)
    rpix = np.sqrt((ind[1] - xc) ** 2 + (ind[0] - yc) ** 2)
    # incidnence angle in radians
    #theta = np.arctan(b * rpix)
    # function of Airy I
    f = 4.0 * F ** 2 / np.pi ** 2
    #phi = 4.0 * np.pi * ne * np.cos(theta) / lbda
    phi2 = 2.0 * np.pi * ne / (lbda * np.sqrt(1 + b ** 2 * rpix ** 2))
    I = C + I0 / ( 1. + f * np.sin(phi2) ** 2 )

    return I


def main():
    
    #################
    # Data as input #
    #################
    
    tdu = pyadhoc.readad3('/home/bepinat/Travail/mission_ohp_1014/test/T251/T251.AD3')
    index = 22
    
    # Initial data plot
    #fig = plt.figure()
    #ax1 = plt.subplot(141)
    #plt.imshow(tdu.data[index,:,:].reshape((512,512)), vmin=290, vmax=2500, cmap='spectral')
    #plt.colorbar(orientation="horizontal")

    # Construction of a flat field for calibration (relie on the hypothesis that the free spectral range is correctly sampled)
    bkg = np.percentile(tdu.data, 0.1)  # background
    flat = np.sum((tdu.data - bkg), axis=0)  # background substraction
    flat[np.where(flat <= 0)] = 1  # remove zeros
    flat /= np.percentile(flat, 99)  # normalization
    #ax1 = plt.subplot(142)
    ##flat = 1
    #plt.imshow(flat, vmin=0, vmax=1, cmap='spectral')
    #plt.colorbar(orientation="horizontal")


#Dans l'ideal, pour trouver les maxima locaux dans un interferogramme, il faudrait
#- faire une lissage spatial des donnees (e.g.gaussien 3x3)
#- calculer le gradient
#- calcul de l'angle du vecteur
#- essayer de faire matcher un pattern de theta par correlation?
#- utiliser les indices (des régions avec les plus forts gradients?) et la direction pour calculer l'intersection des normales?
# par symmetrie, le gradient devrait être faible au centre: si on fait la somme des valeurs absolues des gradients de tous les cannaux, on devrait facilement trouver le centre: minimum de la où le signal est correct

    data = tdu.data[index,:,:].reshape((512,512))
    data2 = ndimage.gaussian_filter(data, 3)  # lissage gaussien de 3 pixels
    #data = (tdu.data[index,:,:].reshape((512,512)) - bkg) / flat + bkg  # flat field correction
    #thr = np.percentile(data, 100)
    #data[np.where(data > thr)] = 0
    #data /= thr
    grad = np.gradient(data2)  # calcul du gradient
    rad = np.sqrt(grad[0] ** 2 + grad[1] ** 2)  # calcul de l'amplitude du gradient
    theta0 = np.arctan2(grad[1], grad[0])  # calcul de la direction du gradient
    theta90 = np.arctan2(grad[0], grad[1])  # idem mais à + pi/2

    plt.imshow(data)
    plt.colorbar()
    plt.show()
    plt.imshow(rad)
    plt.colorbar()
    plt.show()
    plt.imshow(theta90)
    plt.colorbar()
    plt.show()
    
    imtheta0 = np.uint8((theta0 + np.pi) / (2 * np.pi) * 256)
    imtheta90 = np.uint8((theta90 + np.pi) / (2 * np.pi) * 256)
    imrad = np.uint8(rad / np.max(rad) * 256)
    imdata = np.uint8(data2 / np.max(data2) * 256)
    edgestheta0 = cv2.Canny(imtheta0, 252, 256)
    edgestheta90 = cv2.Canny(imtheta90, 252, 256)
    edgesrad = cv2.Canny(imrad, 0, 256)
    edgesdata = cv2.Canny(imdata, 0, 16)
    
    plt.imshow(edgestheta0)
    plt.colorbar()
    plt.show()
    plt.imshow(edgesrad)
    plt.colorbar()
    plt.show()
    plt.imshow(edgesdata)
    plt.colorbar()
    plt.show()
    
    # il faudrait faire une ouverture/dilatation sur edgesrad puis le multiplier par edgestheta pour trouver les anneaux
    
    #grada = np.abs(grad[0]) + np.abs(grad[1])
    #grada /= np.max(grada)
    rad /= np.max(rad)
    extrema = np.where((rad < 0.2) & (edgestheta0 * edgestheta0 != 0))
    img = np.zeros(np.shape(rad))
    img[extrema] = 1
    img[np.where(data2 < np.percentile(data2, 90))] = 0
    
    sector = 5.
    maskr = np.where(rad < np.percentile(rad,75))
    maskt0 = np.where((np.abs(theta0) > (sector * np.pi / 180)) & (np.pi - np.abs(theta0) > (sector * np.pi / 180)) )
    #mask = np.where((rad < np.percentile(rad,75)) | (np.abs(theta0) > ((np.pi / 180) * 90)))
    theta0[maskr] = np.nan
    theta90[maskr] = np.nan
    #plt.imshow(edgesrad, interpolation='nearest')
    
    index = np.indices(np.shape(rad))
    x = np.median(index[1][maskt0])
    y = np.median(index[0][np.where(np.abs(theta90) < np.pi/180)])
    print(x,y)
    
    
    qq = np.where(theta0 < 0)
    theta0[qq] = theta0[qq] + np.pi
    qq = np.where(theta90 < 0)
    theta90[qq] = theta90[qq] + np.pi
    plt.imshow(np.abs(np.cos(theta0)))
    #plt.imshow(np.degrees(theta90), interpolation='nearest', vmin=75, vmax=105)
    #plt.imshow(np.degrees(np.abs((np.abs(theta0) - np.pi / 2))), interpolation='nearest')
    plt.colorbar()
    plt.show()
    #return
    # Flat fielded data plot
    #ax1 = plt.subplot(143)
    #plt.imshow(data, vmin=290, vmax=2500, cmap='spectral')
    #plt.colorbar(orientation="horizontal")
    #plt.show()
    index = np.indices(np.shape(rad))
    xc = np.mean(index[1][np.where(img != 0)])
    yc = np.mean(index[0][np.where(img != 0)])
    print(xc, yc)
    return
    
    #thr = np.percentile(data, 98)
    #data[np.where(data < thr)] = 0
    #data[np.where(data > thr)] = 1
    im = copy.deepcopy(img)
    im0 = np.uint8(im / np.percentile(im,100) * 256)
    edges = cv2.Canny(im0,0,250)
    
    circles = cv2.HoughCircles(im0, cv2.cv.CV_HOUGH_GRADIENT, 2, 100, minRadius=0, maxRadius=300)
    im1 = copy.deepcopy(edges)
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            cv2.circle(im1, (x, y), r, 100)
    print(circles)
    #circ = np.uint8(circles[0][1])
    #cv2.circle(im1, (circ[0], circ[1]), circ[2], 100)
    plt.imshow(im1)
    plt.show()
    
    
    #ax1 = plt.subplot(144)
    #plt.imshow(data, vmin=0, vmax=1, cmap='spectral')
    #plt.colorbar(orientation="horizontal")
    #plt.show()
    return(data)
    
    ## Parameter initialisation
    #lbda = 0.6598
    #pc = 791
    #r1 = (347. - 142.) / 2.
    #r2 = (456. - 33) / 2.
    #b = np.sqrt((2 * pc - 1) / (pc **2 * (r2 ** 2 - r1 ** 2) - 2 * pc * r2 ** 2 + r2 ** 2))
    #ne = lbda * pc * np.sqrt(1 + b ** 2 * r1 ** 2) / 2.    
    
    #f = 4.0 * F ** 2 / np.pi ** 2
    #I0 = (np.percentile(data, 99) - np.percentile(data, 1)) * (1 + f) / f
    #C = np.percentile(data, 99) - I0
    #pi = (I0, C, F, ne, b, xc, yc)
    #print(pi)
    
    ## Constraints on parameters
    ##parbase = {'fixed':1, 'limits':(None, None), 'step':0.1, 'relstep':0.1, 'side':0, 'deriv_reltol':1e-6, 'deriv_abstol':1e-6}
    #parinfo = []
    #parbase = {'fixed':False, 'limits':(I0 * 0.9, I0 * 1.1)}
    #parinfo.append(parbase)
    #parbase = {'fixed':False, 'limits':(C * 0.9, C * 1.1)}
    #parinfo.append(parbase)
    #parbase = {'fixed':False, 'limits':(F / 1.5, F * 1.5)}
    #parinfo.append(parbase)
    #parbase = {'fixed':False, 'limits':(ne - lbda / 4., ne + lbda / 4.)}
    #parinfo.append(parbase)
    #parbase = {'fixed':False, 'limits':(b * 0.96, b * 1.04)}
    #parinfo.append(parbase)
    #parbase = {'fixed':False, 'limits':(xc - 15, xc + 15)}
    #parinfo.append(parbase)
    #parbase = {'fixed':False, 'limits':(yc - 15, yc + 15)}
    #parinfo.append(parbase)
    
    ## Fit
    #pfit, results = mpyfit.fit(least_mpyfit, pi, args=(lbda, x, y, data, flat), parinfo=parinfo, stepfactor=10)
    #print(pfit, results['bestnorm'])
    
    ## Model
    #result = airy2d(I0=pfit[0], C=pfit[1], F=pfit[2], ne=pfit[3], b=pfit[4], xc=pfit[5], yc=pfit[6], lbda=lbda, x=x, y=y)
    
    ## Residualks and plot of residuals
    #residuals = data - result
    #ax1 = plt.subplot(144)
    #plt.imshow(residuals, vmin=-250, vmax=250, cmap='spectral')
    #plt.colorbar(orientation="horizontal")
    #plt.show()
    

if __name__ == "__main__":
    main()
    