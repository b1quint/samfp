import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import astropy.io.fits as fits


def airy1d(I0=1., lamb=0.6563, F=15, n=1, e=100., theta=0):
    f = 4.0 * (F / np.pi) ** 2
    phi = 2 * np.pi * 2 * n * e * np.cos(theta) / lamb
    I = I0 / (1 + f * (np.sin(phi/2)) ** 2)
    #I = (I0 * (tau / (1 - rho)) ** 2)/(1 + 4 * F ** 2 * (np.sin(phi/2)) ** 2 / (np.pi) ** 2)
    return I


def airy2d(I0=1., lamb=0.6563, F=15, n=1, e=1000., fcam=0.1, pix=9., x=512, y=512, xc=256, yc=256):
    '''
    Airy function in order to compute a ring
    
    Parameters
    ----------
    
    I0=1. : float
        intensity
    lamb=0.6563 : float
        wavelength (micron), 
    F=15 : float
        finesse,
    n=1 : float
        reflexion index,
    e=1000. : float
        spacing between the two FP plates (micron), 
    fcam=0.1 : float
        focal length of the camera (meter), 
    pix=9. : float
        pixel size (micron), 
    x=512 : integer
        x-size of the image, 
    y=512 : integer
        y-size of the image,
    xc=256 : float
        ring center x coordinate,
    yc=256 : float
        ring center y coordinate.
        
    Return
    ------
    
    out : ndarray
        An image of a ring with the above parameters given as input
    '''

    # we need the indices of the pixels in image
    ind = np.indices((y,x))
    # we use numpy sqrt function because we compute on arrays
    rpix = np.sqrt((ind[1] - xc) ** 2 + (ind[0] - yc) ** 2)
    # radius unit = meter
    r = rpix * pix * (1.e-6)
    theta = np.arctan(r / fcam)
    # function of Airy I
    I = airy1d(I0=I0, lamb=lamb, F=F, n=n, e=e, theta=theta)
    #f = 4.0 * (F / np.pi) ** 2
    #phi = 2.0 * np.pi * 2 * n * e * np.cos(theta) / lamb
    #I = I0 / ( 1. + f * (np.sin(phi / 2.0)) ** 2 )

    return I

def airy3d(I0=1., lamb=0.6563, F=70, n=1, e=1000., nch=20, de=1., fcam=0.1, pix=9., x=512, y=512, xc=256, yc=256):
    #Est-ce que tu aurais un programme qui crée un cube Fabry-Perot modèle où tu donnes en entrée le nb de canaux, la finesse, le FSR, le centre, etc ?
    #On a un gros pb avec le SOAR, on doit utiliser un étalon bas ordre (p=134) mais sa finesse est de 70 ! Donc je voudrai essayer de simuler si on peut se passer de balayer tout l’interfrange, le pb étant que l’interfrange n’est pas si large que cela ...
    cube = np.zeros((nch, y, x))
    for i in np.arange(nch):
        cube[i,:,:] = airy2d(I0=I0, lamb=lamb, F=F, n=n, e=e + i * de, fcam=fcam, pix=pix, x=x, y=y, xc=xc, yc=yc)
    return cube


def main():
    '''
    '''
    I0 = 1.
    
    # longueur d'onde
    #lamb = 0.6563  # microns
    lamb = 0.6599  # microns
    
    # paramètres instrument/détecteur    
    fac = 2.
    #fcam = 0.203   # 3DNTT
    #fcam = 7 * 0.05   # meters BTFI
    fcam = 0.81   # meters  # SAM
    pix = 9. * fac  # microns 3DNTT
    #pix = 16. * fac  # microns BTFI
    pix = 60. * fac  # microns SAM
    x = 1024 / fac  # taille image x en pixels
    y = 1024 / fac  # taille image y en pixels
    #pix = 15. * fac  # microns SAM
    #x = 4096 / fac  # taille image x en pixels
    #y = 4096 / fac  # taille image y en pixels
    
    # paramètres PF
    n = 1  # optical index
    p = 134  # order
    #p = 609  # order
    F = 70  # finesse
    #F = 22  # finesse
    xc = x/2.  # poxition du centre x
    yc = y/2. # position du centre y
    xc = x/2.-30  # poxition du centre x
    yc = y/2.-20 # position du centre y
    xc = 358 / fac
    yc = 560 /fac
    print(xc, yc)
    
    alpha = 2  # sampling of the FWHM
    
    filename = 'cube.fits'  # nom du fichier de sortie
    
    #paramètres calculés
    nch = int(np.ceil(F * alpha))  # nombre de canaux spectraux pour parcourir tout l'interval spectral (nch peut aussi être fixé si on ne veut pas tout le FSR, auquel cas, il faut commenter la ligne suivante)
    alpha = nch / F  # mise à jour du sampling de la FWHM (pour avoir un nombre de canaux entiers)
    
    e = lamb * p / (2 * n)  # espacement initial
    de = lamb / (2 * alpha * n * F)  # incrément espacement
    
    nch = 100
    fsr = lamb / p
    dl = fsr / 68.    
    de = dl * p / (2 * n)
    print(e, de, lamb, F, n, fcam, pix)
    e = e - 20.5 * de
    #de = lamb / (68 * 2 * n)
    
    # création du cube
    cube = airy3d(I0=I0, lamb=lamb, F=F, n=n, e=e, nch=nch, de=de, fcam=fcam, pix=pix, x=x, y=y, xc=xc, yc=yc)
    
    # enregistrement en fits
    hdu = fits.PrimaryHDU(cube)
    hdulist = fits.HDUList(hdu)
    hdulist.writeto(filename, clobber=True, output_verify='fix')
    
    #for i in range(1000,1010):
        #I=airy2d(e=i)
        #plt.imshow(I)
        #plt.show()

def mainph():
    '''
    '''
    I0 = 200.
    
    # longueur d'onde
    lamb = 0.6563  # microns
    lamb = 0.6599  # microns
    
    # paramètres instrument/détecteur    
    fac = 2
    #fcam = 7 * 0.05   # meters
    fcam = 0.81   # meters
    pix = 60. * fac  # microns
    x = int(1024 / fac)  # taille image x en pixels
    y = int(1024 / fac)  # taille image y en pixels
    
    # paramètres PF
    n = 1  # optical index
    p = 134  # order
    p = 609  # order
    F = 69  # finesse
    xc = x/2.-30  # poxition du centre x
    yc = y/2.-20 # position du centre y
    xc = int(365 / fac)
    yc = int(y - 461 / fac)
    print(xc, yc)
    
    alpha = 1  # sampling of the FWHM
    
    filename = 'cube.fits'  # nom du fichier de sortie
    
    #paramètres calculés
    nch = int(np.ceil(F * alpha))  # nombre de canaux spectraux pour parcourir tout l'interval spectral (nch peut aussi être fixé si on ne veut pas tout le FSR, auquel cas, il faut commenter la ligne suivante)
    alpha = nch / F  # mise à jour du sampling de la FWHM (pour avoir un nombre de canaux entiers)
    
    e = lamb * p / (2 * n)  # espacement initial
    de = lamb / (2 * alpha * n * F)  # incrément espacement
    print(e, de, lamb, F, n, fcam, pix)
    e = e + de / 4
    
    # création du cube
    cube = airy_3d(I0=I0, lamb=lamb, F=F, n=n, e=e, nch=nch, de=de, fcam=fcam, pix=pix, x=x, y=y, xc=xc, yc=yc)
    
    # enregistrement en fits
    hdu = fits.PrimaryHDU(cube)
    hdulist = fits.HDUList(hdu)
    hdulist.writeto(filename, clobber=True, output_verify='fix')
    
    #for i in range(1000,1010):
        #I=airy2d(e=i)
        #plt.imshow(I)
        #plt.show()
        
if __name__ == "__main__":
    mainph()
    main()
