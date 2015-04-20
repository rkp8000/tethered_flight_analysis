__all__ = []

import datetime
import numpy as np
from scipy.stats import zscore

# default header block size
HEADER_BLOCK_SIZE = 2048
# conversion factor from barpos voltage to degree
BARPOS_CONVERSION = 360/5.


def load_edr(fname, header_block_size=HEADER_BLOCK_SIZE, dt=.001,
             lmr_zcore=True, barpos_in_degrees=True):
    """Load header info and data from binary file."""

    if fname[-4:].lower() != '.edr':
        raise ValueError('fname must end with \'.edr\'')

    header = {}

    with open(fname, 'rb') as f:

        # read header data
        end_of_header = False
        while not end_of_header:

            # read next line
            line = f.readline().rstrip()

            # stop if we've moved beyond the header
            if f.tell() <= header_block_size:
                # get key and value of line as correct type
                key, val = line.split('=')

                try:
                    header[key] = int(val)
                except ValueError:
                    try:
                        header[key] = float(val)
                    except ValueError:
                        header[key] = val
            else:
                end_of_header = True

        # get column names
        cols = [header['YN%d'%ii] for ii in range(header['NC'])]

        # get normalization constants from header
        ad = float(header['AD'])
        adcmax = float(header['ADCMAX'] + 1)

        # move to start of binary data
        f.seek(header_block_size)

        # load data into array
        ncols = header['NC']
        nrows = header['NP']/ncols
        data = np.fromfile(f, dtype=np.int16).reshape((nrows, ncols))
        data = data.astype(float)
        # normalize data by calibration, etc.
        for channel in range(ncols):
            ych_channel = 'YCF%d' % channel
            data[:, channel] *= (float(ad) / (adcmax * header[ych_channel]))

        # add time as first column
        time = np.arange(data.shape[0])[:, None] * header['DT']
        data = np.concatenate([time, data], axis=1)
        cols = ['time'] + cols

        # swap frequency & LmR columns
        cols[3], cols[4] = cols[4], cols[3]
        data[:, [3, 4]] = data[:, [4, 3]]

        # downsample data
        if dt > header['DT']:
            downsample_factor = dt/header['DT']
            idxs = np.round(np.arange(data.shape[0], step=downsample_factor))
            idxs = idxs.astype(int)
            if idxs[-1] == data.shape[0]:
                idxs = idxs[:-1]
            data = data[idxs, :]

    if lmr_zcore:
        lampz = zscore(data[:, cols.index('Lamp')])
        rampz = zscore(data[:, cols.index('Ramp')])
        data[:, cols.index('LmR')] = lampz - rampz

    if barpos_in_degrees:
        barpos = data[:, cols.index('Barpos')] * BARPOS_CONVERSION
        barpos[barpos > 180] -= 360
        data[:, cols.index('Barpos')] = barpos

    # create datetime object for file start time
    dt_format = '%m-%d-%Y %I:%M:%S %p'
    file_start_str = header['CTIME']
    file_start = datetime.datetime.strptime(file_start_str, dt_format)

    return data, file_start, cols, header