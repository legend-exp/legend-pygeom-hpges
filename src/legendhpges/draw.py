from __future__ import annotations

import matplotlib.pyplot as plt
from pyg4ometry.visualisation import VtkViewer

from .base import HPGe


def plot_profile(hpge: HPGe, axes: plt.Axes = None, **kwargs) -> (plt.Figure, plt.Axes):
    """Plot the HPGe profile with :mod:`matplotlib`.

    Parameters
    ----------
    hpge
        detector.
    axes
        pre-existing axes where the profile will be plotted.
    **kwargs
        any keyword argument supported by :func:`matplotlib.pyplot.plot`.

    """
    # data
    r = hpge.logical_volume.solid.pR
    z = hpge.logical_volume.solid.pZ
    x = r + [-x for x in reversed(r)]
    y = z + list(reversed(z))

    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    fig = None
    if axes is None:
        fig, axes = plt.subplots()
        fig.tight_layout()
        axes.axis("equal")
        axes.set_xlabel("r [mm]")
        axes.set_ylabel("z [mm]")
        axes.grid()

    default_kwargs = {
        "marker": "o",
        "markersize": 3,
        "markeredgecolor": colors[1],
        "markerfacecolor": colors[1],
        "linewidth": 2,
    }
    default_kwargs |= kwargs

    axes.plot(x, y, **default_kwargs)

    return fig, axes


def visualize(hpge: HPGe, viewer: VtkViewer = None) -> VtkViewer:
    """Visualize the HPGe with :class:`pyg4ometry.visualisation.VtkViewer`.

    Parameters
    ----------
    viewer
        pre-existing VTK viewer.
    """
    if viewer is None:
        viewer = VtkViewer()
    viewer.addLogicalVolume(hpge.logical_volume)
    viewer.view(interactive=True)

    return viewer
