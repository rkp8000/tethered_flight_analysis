import matplotlib.pyplot as plt

from data_handling import load_edr
from view import plot_edr


FNAME = '/Users/rkp/Dropbox/arena_data/edr_files_visual_expt/150422_insect3_tr1.EDR'

data, file_start, cols, header = load_edr(FNAME, dt=.05)

fig, axs = plot_edr(data, cols)

plt.show()