import numpy as np
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt

from math_tools.plot import set_fontsize, set_colors
from math_tools.fun import cdiff
from math_tools.signal import segment_by_threshold as sbt

from data_handling import load_edr


FNAME = '/Users/rkp/Dropbox/arena_data/edr_files_visual_expt/150513_insect6_tr1.EDR'

DT = 0.05
MAXT = 900
MAXTS = int(MAXT/DT)

TPRE = 1
TPOST = 3
TSPRE = int(TPRE/DT)
TSPOST = int(TPOST/DT)

START_INT = 0.6  # s
END_INT = 0.8  # s

# PLOTTING PARAMETERS
FACECOLOR = 'w'
AXCOLOR = 'k'
FONTSIZE = 20
DATA_FIGSIZE = (15, 10)
RESULT_FIGSIZE = (7, 10)
DSTR_FIGSIZE = (10, 10)
TIME_FIGSIZE = (10, 6)
LEFTCOLOR = 'k'
RIGHTCOLOR = 'r'


# get data we're interested in
data, _, cols, _ = load_edr(FNAME, dt=DT)

t = data[:MAXT/DT, cols.index('time')]
freq = data[:MAXT/DT, cols.index('Freq')]
lmr = data[:MAXT/DT, cols.index('LmR')]
barpos = data[:MAXT/DT, cols.index('Barpos')]
barvel = cdiff(barpos)/DT
barspeed = np.abs(barvel)


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
triggered_freqs = triggered_freqs[:octr+1]
triggered_lmrs = triggered_lmrs[:octr+1]
triggered_barspeeds = triggered_barspeeds[:octr+1]

# offset triggered averages by value at start
triggered_freqs -= triggered_freqs[:, [TSPRE]]
triggered_lmrs -= triggered_lmrs[:, [TSPRE]]

# calculate scalar responses
triggered_wbs = triggered_freqs[:, (triggered_t > START_INT)*(triggered_t < END_INT)].sum(1) * DT
triggered_mean_lmrs = triggered_lmrs[:, (triggered_t > START_INT)*(triggered_t < END_INT)].mean(1)

# plot ensembles of bar-movement-onset-triggered behaviors
_, trig_avg_axs = plt.subplots(3, 2, sharex=True, figsize=RESULT_FIGSIZE, facecolor=FACECOLOR, tight_layout=True)

for aidx in range(2):
    if aidx == 0:
        stim_idxs = right_motion_idxs
        c = RIGHTCOLOR
    elif aidx == 1:
        stim_idxs = left_motion_idxs
        c = LEFTCOLOR
    trig_avg_axs[0, aidx].plot(triggered_t, triggered_freqs[stim_idxs, :].T, c='k', lw=1, alpha=.1)
    trig_avg_axs[0, aidx].plot(triggered_t, triggered_freqs[stim_idxs, :].mean(0), c=c, lw=3)

    trig_avg_axs[1, aidx].plot(triggered_t, triggered_lmrs[stim_idxs, :].T, c='k', lw=1, alpha=.1)
    trig_avg_axs[1, aidx].plot(triggered_t, triggered_lmrs[stim_idxs, :].mean(0), c=c, lw=3)

    trig_avg_axs[-1, aidx].plot(triggered_t, triggered_barspeeds[stim_idxs, :].T, c='k', lw=1, alpha=.1)
    trig_avg_axs[-1, aidx].plot(triggered_t, triggered_barspeeds[stim_idxs, :].mean(0), c=c, lw=3)

    trig_avg_axs[0, aidx].set_ylim(-15, 35)
    trig_avg_axs[1, aidx].set_ylim(-3, 3)
    trig_avg_axs[0, aidx].set_ylabel('change in freq (Hz)')
    trig_avg_axs[1, aidx].set_ylabel('change in |L-R| (a.u.)')
    trig_avg_axs[-1, aidx].set_ylabel('barspeed (deg/s)')

    trig_avg_axs[-1, aidx].set_xlabel('time since motion onset (s)')

# plot distributions of scalarized responses to right or left motion
_, dstr_axs = plt.subplots(2, 1, figsize=DSTR_FIGSIZE, facecolor=FACECOLOR, tight_layout=True)

dstr_axs[0].hist([triggered_wbs[right_motion_idxs], triggered_wbs[left_motion_idxs]], bins=15, color=[RIGHTCOLOR, LEFTCOLOR], normed=True)
dstr_axs[1].hist([triggered_mean_lmrs[right_motion_idxs], triggered_mean_lmrs[left_motion_idxs]], bins=15, color=[RIGHTCOLOR, LEFTCOLOR], normed=True)

dstr_axs[0].set_xlabel('change in number of wingbeats')
dstr_axs[0].set_ylabel('probability')
dstr_axs[1].set_xlabel('change in |L-R|')
dstr_axs[1].set_ylabel('probability')

# perform t-test between right motion and left motion triggered wbs
_, p_lr_wbf = ttest_ind(triggered_wbs[right_motion_idxs], triggered_wbs[left_motion_idxs])
_, p_lr_lmr = ttest_ind(triggered_mean_lmrs[right_motion_idxs], triggered_mean_lmrs[left_motion_idxs])

print 'P-value between WBF response to left and right motion: {}'.format(p_lr_wbf)
print 'P-value between LMR response to left and right motion: {}'.format(p_lr_lmr)

for ax in trig_avg_axs.flatten():
    ax.set_xlim(-1, 3)
    set_colors(ax, AXCOLOR)
    set_fontsize(ax, FONTSIZE)

for ax in dstr_axs:
    set_colors(ax, AXCOLOR)
    set_fontsize(ax, FONTSIZE)

plt.show()