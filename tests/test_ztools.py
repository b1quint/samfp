import numpy as np
import os

from samfp.tools import ztools
from scipy import interpolate
from astropy.io import fits

import matplotlib.pyplot as plt
plt.switch_backend('agg')

def test_z_cut():
    """Little method to test the ZCut method"""

    begin = 3
    end = -1
    zcut = ztools.ZCut('tests/test_data/test_ztools.fits', '.temp.fits', n_begin=begin, n_end=end)
    zcut.start()
    zcut.join()

    data = fits.getdata('.temp.fits')
    header = fits.getheader('.temp.fits')

    assert header['CRVAL3'] == 1024
    assert header['CRPIX3'] == 2
    assert header['CDELT3'] == 10

    ref_data = [0, 0, 0, 1, 4, 4, 1, 0, 0, 0]
    ref_data = ref_data[begin:end]

    for i in range(len(ref_data)):
        assert data[i, 0, 0] == ref_data[i]

    os.remove('.temp.fits')


def test_linear_interpolation():

    data = [0, 0, 0, 1, 4, 4, 1, 0, 0, 0]

    s = np.array(data)
    z = np.arange(s.size)

    s = np.hstack((s[s.size // 2:], s, s[:s.size // 2]))
    z = np.hstack((z[z.size // 2:] - z.size, z, z[:z.size // 2] + z.size))

    f = interpolate.interp1d(z, s, kind='linear')
    zo = f(z)

    assert (np.abs(np.sum(zo - s)) / s.sum() < 0.1)


def test_z_oversample():

    oversample = ztools.ZOversample('tests/test_data/test_ztools.fits', 'dummy.fits', 4)
    oversample.start()
    oversample.join()

    data = fits.getdata('tests/test_data/test_ztools.fits')
    assert (np.abs(data.sum() - oversample.results.sum()) / data.sum() < 0.1)
    assert (data.size * 4 == oversample.results.size)

    os.remove('dummy.fits')


def test_z_repeat_after():

    data = np.array([10, 20, 15])
    data = np.reshape(data, (3, 1, 1))

    h = fits.Header()
    h['CRPIX3'] = 1
    h['CRVAL3'] = 1
    h['CDELT3'] = 1

    repeat = ztools.ZRepeat(n_after=1)
    repeat.data = data
    repeat.header = h
    repeat._original_depth = data.shape[0]

    repeat.get_data_shape()
    repeat.repeat_data()

    temp_y = [10, 20, 15, 10, 20, 15]
    for i in range(6):
         assert repeat.data[i, 0, 0] == temp_y[i]

    repeat.fix_header()
    assert repeat.header['CRPIX3'] == 1


def test_z_repeat_before():

    data = np.array([10, 20, 15])
    data = np.reshape(data, (3, 1, 1))

    h = fits.Header()
    h['CRPIX3'] = 1
    h['CRVAL3'] = 1
    h['CDELT3'] = 1

    repeat = ztools.ZRepeat(n_before=1)
    repeat.data = data
    repeat.header = h
    repeat._original_depth = data.shape[0]

    repeat.get_data_shape()
    repeat.repeat_data()

    temp_y = [10, 20, 15, 10, 20, 15]
    for i in range(6):
         assert repeat.data[i, 0, 0] == temp_y[i]

    repeat.fix_header()
    assert repeat.header['CRPIX3'] == (data.shape[0] + 1)


def test_z_repeat_both():

    data = np.array([10, 20, 15])
    data = np.reshape(data, (3, 1, 1))

    h = fits.Header()
    h['CRPIX3'] = 1
    h['CRVAL3'] = 1
    h['CDELT3'] = 1

    repeat = ztools.ZRepeat(n_before=1, n_after=1)
    repeat.data = data
    repeat.header = h
    repeat._original_depth = data.shape[0]

    repeat.get_data_shape()
    repeat.repeat_data()

    temp_y = [10, 20, 15, 10, 20, 15]
    for i in range(6):
         assert repeat.data[i, 0, 0] == temp_y[i]

    repeat.fix_header()
    assert repeat.header['CRPIX3'] == (data.shape[0] + 1)


def test_z_roc():
    """Testing the whole repeat-oversample-cut method"""

    filename = 'tests/test_data/test_ztools.fits'
    repeated_data_filename = '.zrep_temp.fits'
    oversampled_data_filename = '.zosample_temp.fits'
    final_filename = '.temp.fits'
    factor = 5

    repeat = ztools.ZRepeat(filename, repeated_data_filename, n_before=1, n_after=1)
    repeat.start()
    repeat.join()

    oversample = ztools.ZOversample(repeated_data_filename, oversampled_data_filename, factor)
    oversample.start()
    oversample.join()

    cut = ztools.ZCut(oversampled_data_filename,final_filename,
                      n_begin=repeat._original_depth * oversample.oversample_factor * 1,
                      n_end=-repeat._original_depth * oversample.oversample_factor * 1)
    cut.start()
    cut.join()

    hdu = fits.open(filename)[0]
    h = hdu.header
    y = hdu.data[:, 0, 0]
    x = (np.arange(h['NAXIS3']) + 1 - h['CRPIX3']) * h['CDELT3'] + h['CRVAL3']

    hdu_r = fits.open(repeated_data_filename)[0]
    h_r = hdu_r.header
    y_r = hdu_r.data[:, 0, 0]
    x_r = (np.arange(h_r['NAXIS3']) + 1 - h_r['CRPIX3']) * h_r['CDELT3'] + h_r['CRVAL3']

    hdu_o = fits.open(oversampled_data_filename)[0]
    h_o = hdu_o.header
    y_o = hdu_o.data[:, 0, 0]
    x_o = (np.arange(h_o['NAXIS3']) + 1 - h_o['CRPIX3']) * h_o['CDELT3'] + h_o['CRVAL3']

    hdu_c = fits.open(final_filename)[0]
    h_c = hdu_c.header
    y_c = hdu_c.data[:, 0, 0]
    x_c = (np.arange(h_c['NAXIS3']) + 1 - h_c['CRPIX3']) * h_c['CDELT3'] + h_c['CRVAL3']

    plt.plot(x, y, 'C0o', label='Original data')
    plt.plot(x_r, y_r - 0.1, 'C1+', label='Repeated data')
    plt.plot(x_o, y_o - 0.2, 'C2x', alpha=0.5, label='Normalized and oversampled data')
    plt.plot(x_c, y_c, 'C3v', alpha=0.5, label='Cut, normalized and oversampled data')

    plt.ylim(-2, 4.5)
    plt.legend(loc='best')
    plt.savefig('.temp.png')
