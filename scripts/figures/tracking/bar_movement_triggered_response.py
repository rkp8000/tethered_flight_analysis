import numpy as np
import matplotlib.pyplot as plt

from math_tools.plot import set_fontsize, set_colors
from math_tools.fun import cdiff
from math_tools.signal import segment_by_threshold as sbt

from data_handling import load_edr


FNAME = '/Users/rkp/Dropbox/arena_data/edr_files_visual_expt/150513_insect15_tr1.EDR'

DT = 0.05
MAXT = 700
MAXTS = int(MAXT/DT)

TPRE = 1
TPOST = 3
TSPRE = int(TPRE/DT)
TSPOST = int(TPOST/DT)

# PLOTTING PARAMETERS
FACECOLOR = 'k'
AXCOLOR = 'w'
FONTSIZE = 24
DATA_FIGSIZE = (15, 10)
RESULT_FIGSIZE = (7, 10)


# get data we're interested in
data, _, cols, _ = load_edr(FNAME, dt=DT)

t = data[:MAXT/DT, cols.index('time')]
freq = data[:MAXT/DT, cols.index('Freq')]
lmr = data[:MAXT/DT, cols.index('LmR')]
barpos = data[:MAXT/DT, cols.index('Barpos')]
barvel = cdiff(barpos)/DT
barspeed = np.abs(barvel)


# plot entire data series
_, data_axs = plt.subplots(4, 1, sharex=True, figsize=DATA_FIGSIZE, facecolor=FACECOLOR, tight_layout=True)

data_axs[0].plot(t, freq, lw=2)
data_axs[1].plot(t, lmr, lw=2)
data_axs[2].plot(t, barpos, lw=2)
data_axs[3].plot(t, barspeed, lw=2)

data_axs[0].set_ylabel('freq (Hz)')
data_axs[1].set_ylabel('L - R')
data_axs[2].set_ylabel('bar position')
data_axs[2].set_ylabel('bar speed')

data_axs[-1].set_xlabel('time (s)')


# get all indices of times when bar started moving
_, onsets, offsets, _ = sbt(barspeed, th=5).T

# get triggered frequencies, etc.
triggered_freqs = np.zeros((len(onsets), TSPRE + TSPOST))
triggered_lmrs = np.zeros((len(onsets), TSPRE + TSPOST))
triggered_barvels = np.zeros((len(onsets), TSPRE + TSPOST))
triggered_barspeeds = np.zeros((len(onsets), TSPRE + TSPOST))
triggered_t = np.arange(-TPRE, TPOST, DT)

# also store what kind of onset each one was
left_motion_idxs = []
right_motion_idxs = []

for octr, onset in enumerate(onsets):
    if onset < MAXTS - TSPOST:
        triggered_freqs[octr, :] = freq[onset - TSPRE:onset + TSPOST]
        triggered_lmrs[octr, :] = np.abs(lmr[onset - TSPRE:onset + TSPOST])
        triggered_barvels[octr, :] = barvel[onset - TSPRE:onset + TSPOST]
        triggered_barspeeds[octr, :] = barspeed[onset - TSPRE:onset + TSPOST]

        if triggered_barvels[octr, :].mean() > 0:
            right_motion_idxs += [octr]
        elif triggered_barvels[octr, :].mean() < 0:
            left_motion_idxs += [octr]
    else:
        break

# remove unused triggered behaviors
triggered_freqs = triggered_freqs[:octr]
triggered_lmrs = triggered_lmrs[:octr]
triggered_barspeeds = triggered_barspeeds[:octr]

# offset triggered averages by value at start
triggered_freqs -= triggered_freqs[:, [TSPRE]]
triggered_lmrs -= triggered_lmrs[:, [TSPRE]]


# plot ensembles of bar-movement-onset-triggered behaviors
_, trig_avg_axs = plt.subplots(3, 1, sharex=True, figsize=RESULT_FIGSIZE, facecolor=FACECOLOR, tight_layout=True)

trig_avg_axs[0].plot(triggered_t, triggered_freqs.T, c='k', lw=1, alpha=.1)
trig_avg_axs[0].plot(triggered_t, triggered_freqs.mean(0), c='b', lw=3)

trig_avg_axs[1].plot(triggered_t, triggered_lmrs.T, c='k', lw=1, alpha=.1)
trig_avg_axs[1].plot(triggered_t, triggered_lmrs.mean(0), c='b', lw=3)

trig_avg_axs[-1].plot(triggered_t, triggered_barspeeds.T, c='k', lw=1, alpha=.1)
trig_avg_axs[-1].plot(triggered_t, triggered_barspeeds.mean(0), c='b', lw=3)

trig_avg_axs[0].set_ylabel('change in freq (Hz)')
trig_avg_axs[1].set_ylabel('change in |L-R|')
trig_avg_axs[-1].set_ylabel('barspeed (deg/s)')

trig_avg_axs[-1].set_xlabel('time since motion onset (s)')


# clean up plots
for ax in data_axs:
    set_colors(ax, AXCOLOR)
    set_fontsize(ax, FONTSIZE)

for ax in trig_avg_axs:
    ax.set_xlim(-1, 3)
    set_colors(ax, AXCOLOR)
    set_fontsize(ax, FONTSIZE)

plt.show()