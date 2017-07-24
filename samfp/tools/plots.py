import numpy as np
import matplotlib.pyplot as plt


def free_spectral_range(x, y, s, fsr):

    mid = np.median(y)
    std = np.std(y)

    fig = plt.figure()
    fig.canvas.set_window_title("Finding Free-Spectral-Range")

    ax = fig.add_subplot(111)
    ax.set_title("Finding the Free-Spectral-Range")
    ax.plot(x, y, 'ko', label='Measured data')
    ax.plot(x, s(x), 'k-', lw=2, label='3rd deg spline fitting')
    ax.set_xlabel("z [channels]")
    ax.set_ylabel(u"$\\frac{\sum_{x,y} |\Phi(x, y, z) - \Phi(x, y, 0)|}{n_{x,y}}$")

    ax.axhline(mid, ls='-', c='r', alpha=0.5)
    ax.axhline(mid - std, ls='--', c='r', alpha=0.25)
    ax.axhline(mid + std, ls='--', c='r', alpha=0.25)

    ax.axvline(x=(x[fsr-1]), ls='-', c='blue',
                label='Free-Spectral-Range \nat z = %.1f channel' % fsr)

    ax.legend(loc='best')
    ax.set_xlim(x[0], x[-1])
    ax.grid()
    fig.tight_layout()
    plt.show()


def plot_with_vlines(x, y, xpos):
    """
    Plots X and Y and add a dashed line to the xpositions.

    Parameters
    ----------
    x (array_like) : x array to be plot.
    y (array_like) : y array to be plot.
    xpos (array_like) : one or more positions where the vlines will be added.
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.plot(x, y, 'ko')
    for _x in xpos:
        ax.axvline(_x, linestyle="--", color="k")

    plt.show()


def show_divergent_map(data):
    plt.imshow(data, origin='lower', interpolation='nearest', cmap='RdYlBu')
    plt.show()


def show_image(data, cmap, title):

    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.imshow(data, origin='lower', interpolation='nearest', cmap=cmap)
    ax.set_title(title)
    ax.grid()
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    fig.tight_layout()
    plt.show()