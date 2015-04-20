import matplotlib.pyplot as plt


def plot_edr(data, cols, subplot_kw=None, ax_kw=None):
    """Plot data from edr file."""

    if not subplot_kw:
        subplot_kw = {}
    if not ax_kw:
        ax_kw = {}

    naxs = data.shape[1] - 1 # time doesn't get its own plot

    fig, axs = plt.subplots(naxs, 1, sharex=True, tight_layout=True, **subplot_kw)

    t = data[:, 0]

    for actr, ax in enumerate(axs):
        ax.plot(t, data[:, actr + 1], **ax_kw)
        ax.set_ylabel(cols[actr + 1])

    axs[-1].set_xlabel('time (s)')

    return fig, axs