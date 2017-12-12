import itertools
import logging
import numpy as np
import multiprocessing
import threading
import sys

from astropy.io import fits
from scipy import interpolate

from . import io, version

log = io.MyLogger(__name__)

__all__ = ['ZCut', 'ZOversample', 'ZRepeat', 'OverSampler']


# noinspection PyUnusedLocal,PyUnusedLocal
def signal_handler(s, frame):
    sys.exit()


class ZCut(threading.Thread):
    """
    Extract a part of the data-cube in the spectral direction and keeping the
    whole spatial pixels. The header is updated to maintain the calibration
    in the same direction.

    Parameters
    ----------
        _input : str
            The input cube filename.

        _output : str
            The output cube filename.

        n_begin : int
            The channel that will be considered as the first new one
            (inclusive).

        n_end : int
            The channel that will be considered as the last new one
            (exclusive).
    """
    def __init__(self, _input, _output, n_begin=None, n_end=None):

        threading.Thread.__init__(self)

        self._input = _input
        self._output = _output
        self.n_begin = n_begin
        self.n_end = n_end

    def run(self):

        log.info("")
        log.info("SAM-FP Tools: fp_cut")
        log.info("by Bruno Quint (bquint@ctio.noao.edu)")
        log.info("version {:s}".format(version.__str__))
        log.info("Starting program.")
        log.info("")

        data = fits.getdata(self._input)
        header = fits.getheader(self._input)

        self.n_begin = 0 if self.n_begin is None else self.n_begin
        self.n_end = header['NAXIS3'] if self.n_end is None else self.n_end

        self._original_depth = data.shape[0]

        data = data[self.n_begin:self.n_end]
        header['CRPIX3'] -= self.n_begin

        self._depth = data.shape[0]

        header.set(
            'ZC_ORSIZ',
            value=self._original_depth,
            comment='Cube depth before trim.'
        )

        header.set(
            'ZC_AFSIZ',
            value=self._depth,
            comment='Cube depth after trim.',
            after='ZC_ORSIZ'
        )

        header.set(
            'ZC_BEGIN',
            value=self.n_begin,
            comment='# channels removed from beginning.',
            after='ZC_AFSIZ'
        )

        header.set(
            'ZC_END',
            value=self.n_end,
            comment='# channels removed from end.',
            after='ZC_BEGIN'
        )

        header.add_blank('--- Cube Z Cut ---', before='ZC_ORSIZ')
        header.add_blank('', after='ZC_END')

        fits.writeto(self._output, data, header)
        log.info('Done.')
        log.info('')


class ZOversample(threading.Thread):
    """
    Oversample a data-cube in the spectral direction using linear fitting.

    Parameters
    ----------
        _input : str
            The input cube filename

        _output : str
            The output cube filename

        oversample_factor : int
            The oversample factor. In other words, how many points will be added
            for each original point.

    Optional Arguments
    ------------------
        kind : str
            The oversample algorithm. The only option available now is linear interpolation but this is here to allow
            future implementation of other options.
    """
    def __init__(self, _input, _output, oversample_factor, kind='linear'):

        threading.Thread.__init__(self)

        self.input = _input
        self.output = _output
        self.oversample_factor = oversample_factor
        self.kind = kind

        self._depth = None
        self._original_depth = None

    def run(self):

        log.info("")
        log.info("SAM-FP Tools: fp_oversample")
        log.info("by Bruno Quint (bquint@ctio.noao.edu)")
        log.info("version {:s}".format(version.__str__))
        log.info("Starting program.")
        log.info("")

        data = fits.getdata(self.input)
        header = fits.getheader(self.input)

        depth, height, width = data.shape

        log.info("Cube depth before oversample: {:d}".format(depth))

        new_depth = self.oversample_factor * depth
        log.info("Cube depth after oversample: {:d}".format(new_depth))
        del data

        self._original_depth = depth
        self._depth = new_depth

        x = np.arange(header['NAXIS1'], dtype=int)
        y = np.arange(header['NAXIS2'], dtype=int)

        # Keep the terminal alive
        loading = multiprocessing.Process(target=stand_by, name="stand_by")
        loading.start()

        # Create a pool for subprocesses
        p = multiprocessing.Pool(4)
        results = None
        fitter = OverSampler(self.input, self.oversample_factor, kind=self.kind)

        try:
            results = p.map_async(fitter, itertools.product(x, y)).get(99999999)
        except KeyboardInterrupt:
            print('\n\nYou pressed Ctrl+C!')
            print('Leaving now. Bye!\n')
            pass

        # Closing processes
        p.close()
        p.join()
        loading.terminate()

        header = self.fix_header(header)

        results = np.array(results)
        results = results.reshape((width, height, new_depth))
        results = np.transpose(results, axes=[2, 1, 0])
        self.results = results

        fits.writeto(self.output, results, header)
        log.info('Done.')
        log.info('')

    def fix_header(self, header):

        o = self.oversample_factor
        x = (np.arange(self._original_depth) - header['CRPIX3'] + 1) \
            * header['CDELT3'] + header['CRVAL3']

        new_x = np.linspace(x[0], x[-1] + (o - 1) / o, o * x.size)
        delta_x = np.mean(new_x[1:] - new_x[:-1])

        keys = ['PHMSAMP', 'C3_3', 'CDELT3']
        for key in keys:
            try:
                header.set(
                    key,
                    value = delta_x,
                    after='CRVAL3'
                )
            except KeyError:
                pass

        header['CRPIX3'] = np.argmin(np.abs(new_x - header['CRVAL3'])) + 1

        header.set(
            'ZO_OVFAC',
            value=self.oversample_factor,
            comment='Oversample factor.'
        )

        header.set(
            'ZO_ORSIZ',
            value=self._original_depth,
            comment='Cube depth before oversample',
            after='ZO_OVFAC'
        )

        header.set(
            'ZO_AFSIZ',
            value=self._depth,
            comment='Cube depth after oversample.',
            after='ZO_ORSIZ'
        )

        header.add_blank('--- Cube Z Oversample ---', before='ZO_OVFAC')
        header.add_blank('', after='ZO_AFSIZ')

        return header

class ZRepeat(threading.Thread):
    """
    Repeat a data-cube in the spectral direction (Z).
    """
    def __init__(self, _input=None, _output=None, n_before=0, n_after=0):
        threading.Thread.__init__(self)

        self.input = _input
        self.output = _output
        self.n_before = n_before
        self.n_after = n_after

        self.data = None
        self.header = None

        self._width = None
        self._height = None
        self._depth = None
        self._original_depth = None

    def run(self):
        self.print_initial_info()
        self.read_data()
        self.repeat_data()
        self.fix_header()
        self.write()

    def fix_header(self):

        self.get_data_shape()

        self.header['CRPIX3'] += self.n_before * self._original_depth

        self.header.set(
            'ZR_ORSIZ',
            value=self._original_depth,
            comment='Original cube depth before repeating Z.'
        )

        self.header.set(
            'ZR_AFSIZ',
            value=self._depth,
            comment='Cube depth after repeating Z.',
            after='ZR_ORSIZ'
        )

        self.header.set(
            'ZR_COPBE',
            value=self.n_before,
            comment='# copies of the cube at its beginning.',
            after='ZR_AFSIZ'
        )

        self.header.set(
            'ZR_CHBEF',
            value=self._original_depth * self.n_before,
            comment='# channels added at the beginning of the cube.',
            after='ZR_COPBE'
        )

        self.header.set(
            'ZR_COPEN',
            value=self.n_after,
            comment='# copies of the cube at its end.',
            after='ZR_CHBEF'
        )

        self.header.set(
            'ZR_CHEND',
            value=self._original_depth * self.n_after,
            comment='# channels added to the end of the cube.',
            after='ZR_COPEN'
        )

        self.header.add_blank('--- Cube Repeat ---', before='ZR_ORSIZ')
        self.header.add_blank('', after='ZR_CHEND')

    def print_initial_info(self):
        log.info("")
        log.info("SAM-FP Tools: fp_repeat")
        log.info("by Bruno Quint (bquint@ctio.noao.edu)")
        log.info("version {:s}".format(version.__str__))
        log.info("Starting program.")
        log.info("")

        log.info('Read data from: {0.input:s}'.format(self))
        log.info('Write file to: {0.output:s}'.format(self))
        log.info('Add {0.n_before:d} FSR at the beginning of the cube'.format(self))
        log.info('Add {0.n_after:d} FSR at the end the cube'.format(self))

    def read_data(self):
        """
        Read the data and store it and its metadate for header manipulation.
        """
        self.data = fits.getdata(self.input)
        self.header = fits.getheader(self.input)

        self.get_data_shape()

        self._original_depth = self._depth

    def get_data_shape(self):
        d, w, h = self.data.shape

        self._depth = d
        self._height = h
        self._width = w

    def repeat_data(self):

        i = 0
        temp_before = self.data
        while i < self.n_before:
            temp_before = np.vstack((self.data, temp_before))
            i += 1

        i = 0
        temp_after = temp_before
        while i < self.n_after:
            temp_after = np.vstack((temp_after, self.data))
            i += 1

        self.data = temp_after

    def write(self):
        fits.writeto(self.output, self.data, self.header)
        log.info('Done.')
        log.info('')


class OverSampler:

    def __init__(self, filename, oversample_factor, kind='linear'):
        """
        Parameter
        ---------

            filename : str
                Relative or absolute path to the file that contains a data-cube
                from where the 2D maps will be extracted through gaussian
                fitting.

            oversample_factor : int
                The oversample factor. This actually means how many elements each old element will provide
                (e.g., an array with 10 elements with oversample of 3 will have 30 elements).

        Optional Arguments
        ------------------
            kind : str

        """
        self._filename = filename
        self.oversample_factor = oversample_factor

        # Load the data
        self.data = fits.getdata(self._filename, memmap=True)

        # Load the relevant values from the header
        h = fits.getheader(self._filename)
        self.z_start = h['CRVAL3']
        self.z_ref = h['CRPIX3']

        try:
            self.z_delta = h['CDELT3']
        except KeyError:
            self.z_delta = h['C3_3']

        self.kind = kind

    def __call__(self, indexes):
        """
        Parameter
        ---------
            indexes : tuple
                Contains two integers that correspond to the X and Y indexes
                that will be used to extract the spectrum from the data-cube and
                fits a gaussian to this extracted spectrum.
        Returns
        -------
            results : ?
        """
        i, j = indexes

        s = self.data[:, j, i] # Spectrum

        if self.kind == 'linear':
            new_s = self.linear_interpolation(s)

        return new_s

    def linear_interpolation(self, y):

        x = np.arange(y.size)

        y_ext = np.hstack(
            (y[y.size // 2:], y, y[:y.size // 2])
        )

        x_ext = np.hstack(
            (x[x.size // 2:] - x.size, x, x[:x.size // 2] + x.size)
        )

        f = interpolate.interp1d(x_ext, y_ext, kind='linear')

        o = self.oversample_factor
        new_x = np.linspace(x[0], x[-1] + (o - 1) / o, o * x.size)
        new_y = f(new_x) / self.oversample_factor
        # new_y = new_y[y.size * o // 4:-y.size * o // 4]

        return new_y


def stand_by(level=logging.NOTSET):
    """
    A silly method that keeps the terminal alive so the user knows that
    this programs is still running. :-)
    """
    from time import sleep

    output = ['/', '-', '\\', '|']
    i = 0

    if level in [logging.NOTSET, logging.WARN, logging.ERROR]:
        return

    while True:
        sys.stdout.write("\r [{:s}]".format(output[i]))
        sys.stdout.flush()
        sleep(0.5)
        i += 1
        i %= 4

    return
