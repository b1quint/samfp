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

        if self.n_begin is not None:
            data = data[self.n_begin:]
            header['CRPIX3'] -= (self.n_begin + 1)
        else:
            self.n_begin = 0

        if self.n_end is not None:
            data = data[:self.n_end]
        else:
            self.n_end = data.shape[0]

        header.add_history('Cube cut from z = %i to z = %i' %
                           (self.n_begin, self.n_end))

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

    def fix_header(self, header=None):

        keys = ['CDELT3', 'C3_3', 'PHMSAMP']
        for key in keys:
            try:
                header[key] /= self.oversample_factor
            except KeyError:
                pass

        header.set('3DOVS_O', value=self.oversample_factor, comment='Oversample factor.')
        header.add_blank('--- Cube Z Oversample ---', before='3DOVS_O')
        header.add_blank('', after='3DOVS_O')

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

    def run(self):
        self.print_initial_info()
        self.read_data()
        self.repeat_data()
        self.fix_header()
        self.write()

    def fix_header(self):
        self.header['CRPIX3'] += self.n_before * self._depth

        self.header.set('3DREP_B', value=self.n_before, comment='Number of copies of the cube at its beginning.')
        self.header.set('3DREP_A', value=self.n_after, comment='Number of copies of the cube at its end.', after='3DREP_B')
        self.header.add_blank('--- Cube Repeat ---', before='3DREP_B')
        self.header.add_blank('', after='3DREP_A')

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
        self.data = fits.getdata(self.input)
        self.header = fits.getheader(self.input)
        self.get_data_shape()

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

        y = np.hstack((y[y.size // 2:], y, y[:y.size // 2]))
        x = np.hstack((x[x.size // 2:] - x.size, x, x[:x.size // 2] + x.size))

        f = interpolate.interp1d(x, y, kind='linear')

        o = self.oversample_factor
        new_x = np.linspace(x[0], x[-1] + (o - 1) / o, o * x.size)
        new_y = f(new_x) / self.oversample_factor
        new_y = new_y[y.size * o // 4:-y.size * o // 4]

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