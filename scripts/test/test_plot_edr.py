import matplotlib.pyplot as plt

from data_handling import load_edr
from view import plot_edr


FNAME = '/Users/rkp/Dropbox/arena_data/edr_files_visual_expt/150415_insect2_just_visual.EDR'

data, file_start, cols, header = load_edr(FNAME, dt=.001)

fig, axs = plot_edr(data, cols)

plt.show()