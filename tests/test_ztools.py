import numpy as np

from samfp.tools import ztools
from scipy import interpolate
from astropy.io import fits


def _test_z_cut():
    """Little method to test the ZCut method"""
    assert True


def _test_linear_interpolation():

    data = [0, 0, 0, 1, 4, 4, 1, 0, 0, 0]

    s = np.array(data)
    z = np.arange(s.size)

    s = np.hstack((s[s.size // 2:], s, s[:s.size // 2]))
    z = np.hstack((z[z.size // 2:] - z.size, z, z[:z.size // 2] + z.size))

    f = interpolate.interp1d(z, s, kind='linear')
    zo = f(z)

    assert (np.abs(np.sum(zo - s)) / s.sum() < 0.1)


def _test_z_oversample():

    oversample = ztools.ZOversample('tests/test_data/test_000.fits', 'dummy.fits', 4)
    oversample.start()
    oversample.join()

    data = fits.getdata('tests/test_data/test_000.fits')
    assert (np.abs(data.sum() - oversample.results.sum()) / data.sum() < 0.1)
    assert (data.size * 4 == oversample.results.size)


def _test_z_repeat_after():

    data = np.array([10, 20, 15])
    data = np.reshape(data, (3, 1, 1))

    h = fits.Header()
    h['CRPIX3'] = 1
    h['CRVAL3'] = 1
    h['CDELT3'] = 1

    repeat = ztools.ZRepeat(n_after=1)
    repeat.data = data
    repeat.header = h

    repeat.get_data_shape()
    repeat.repeat_data()

    temp_y = [10, 20, 15, 10, 20, 15]
    for i in range(6):
         assert repeat.data[i, 0, 0] == temp_y[i]

    repeat.fix_header()
    assert repeat.header['CRPIX3'] == 1


def _test_z_repeat_before():

    data = np.array([10, 20, 15])
    data = np.reshape(data, (3, 1, 1))

    h = fits.Header()
    h['CRPIX3'] = 1
    h['CRVAL3'] = 1
    h['CDELT3'] = 1

    repeat = ztools.ZRepeat(n_before=1)
    repeat.data = data
    repeat.header = h

    repeat.get_data_shape()
    repeat.repeat_data()

    temp_y = [10, 20, 15, 10, 20, 15]
    for i in range(6):
         assert repeat.data[i, 0, 0] == temp_y[i]

    repeat.fix_header()
    assert repeat.header['CRPIX3'] == (data.shape[0] + 1)


def _test_z_repeat_both():

    data = np.array([10, 20, 15])
    data = np.reshape(data, (3, 1, 1))

    h = fits.Header()
    h['CRPIX3'] = 1
    h['CRVAL3'] = 1
    h['CDELT3'] = 1

    repeat = ztools.ZRepeat(n_before=1, n_after=1)
    repeat.data = data
    repeat.header = h

    repeat.get_data_shape()
    repeat.repeat_data()

    temp_y = [10, 20, 15, 10, 20, 15]
    for i in range(6):
         assert repeat.data[i, 0, 0] == temp_y[i]

    repeat.fix_header()
    assert repeat.header['CRPIX3'] == (data.shape[0] + 1)


def _test_z_roc():
    """Testing the whole repeat-oversample-cut method"""
    assert True

