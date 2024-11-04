from __future__ import annotations

import json
import logging
import math
from abc import ABC, abstractmethod
from pathlib import Path

import numpy as np
from legendmeta import AttrsDict
from numpy.typing import ArrayLike, NDArray
from pint import Quantity
from pyg4ometry import geant4

from . import utils
from .materials import make_natural_germanium
from .registry import default_g4_registry
from .registry import default_units_registry as u


class HPGe(ABC, geant4.LogicalVolume):
    """An High-Purity Germanium detector.

    Parameters
    ----------
    metadata
        LEGEND HPGe configuration metadata file name describing the
        detector shape.
    name
        name to attach to this detector. Used to name solid and logical
        volume.
    registry
        pyg4ometry Geant4 registry instance.
    material
        pyg4ometry Geant4 material for the detector.
    """

    def __init__(
        self,
        metadata: str | dict | AttrsDict,
        name: str | None = None,
        registry: geant4.Registry = default_g4_registry,
        material: geant4.MaterialCompound = None,
    ) -> None:
        if registry is None:
            msg = "registry cannot be None"
            raise ValueError(msg)

        if metadata is None:
            msg = "metadata cannot be None"
            raise ValueError(msg)

        if material is None:
            material = make_natural_germanium(registry)

        # build crystal, declare as detector
        if not isinstance(metadata, (dict, AttrsDict)):
            with Path(metadata).open() as jfile:
                self.metadata = AttrsDict(json.load(jfile))
        else:
            self.metadata = AttrsDict(metadata)

        if name is None:
            self.name = self.metadata.name
        else:
            self.name = name

        self.registry = registry

        self.surfaces = []

        # build logical volume, default [mm]
        super().__init__(self._g4_solid(), material, self.name, self.registry)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.metadata})"

    def _g4_solid(self) -> geant4.solid.SolidBase:
        """Build (by default) a :class:`pyg4ometry.solid.GenericPolycone` instance from the (r, z) information.

        Returns
        -------
        g4_solid
            A derived class of :class:`pyg4ometry.solid.SolidBase` to be used to construct the logical volume.

        Note
        ----
            Detectors with a special geometry can have this method overridden in their class definition.
        """
        # return ordered r,z lists, default unit [mm]
        r, z = self._decode_polycone_coord()

        # build generic polycone, default [mm]
        return geant4.solid.GenericPolycone(
            self.name, 0, 2 * math.pi, r, z, self.registry
        )

    @abstractmethod
    def _decode_polycone_coord(self) -> tuple[list[float], list[float]]:
        """Decode shape information from geometry dictionary into (r, z) coordinates.

        Suitable for building a :class:`G4GenericPolycone`.

        Returns
        -------
        (r, z)
            two lists of r and z coordinates, respectively.

        Note
        ----
        Must be overloaded by derived classes.
        """

    def get_profile(self) -> tuple[list[float], list[float]]:
        """Get the profile of the HPGe detector.

        Returns
        -------
        (r.z)
            two lists of r and z coordinates, respectively.

        Note
        -----
            For V02160A and P00664A the detector profile is that of the solid without cut.
        """
        if isinstance(self.solid, geant4.solid.GenericPolycone) is False:
            r = self.solid.obj1.pR
            z = self.solid.obj1.pZ
        else:
            r = self.solid.pR
            z = self.solid.pZ
        return r, z

    def is_inside(self, coords: ArrayLike, tol: float = 1e-11) -> NDArray[bool]:
        """Compute whether each point is inside the shape

        Parameters
        ----------
        coords
            2D array of shape `(n,3)` of `(x,y,z)` coordinates for each of `n` points, second index corresponds to `(x,y,z)`.
        tol
            distance outside the surface which is considered inside.

        Returns
        -------
        numpy array of booleans.
        """

        if isinstance(self.solid, geant4.solid.GenericPolycone) is False:
            msg = f"distance_to_surface is not implemented for {type(self.solid)} yet"
            raise NotImplementedError(msg)

        if isinstance(self.solid, geant4.solid.GenericPolycone) is False:
            msg = f"distance_to_surface is not implemented for {type(self.solid)} yet"
            raise NotImplementedError(msg)

        if not isinstance(coords, np.ndarray):
            coords = np.array(coords)

        if np.shape(coords)[1] != 3:
            msg = "coords must be provided as a 2D array with x,y,z coordinates for each point."
            raise ValueError(msg)

        # get the coordinates
        r, z = self.get_profile()

        dists = utils.get_distance_vectors(coords, r, z, surface_indices=None, tol=tol)

        ids = np.argmin(abs(dists), axis=1)

        return np.where(dists[np.arange(dists.shape[0]), ids] > 0, True, False)

    def distance_to_surface(
        self, coords: ArrayLike, surface_indices: ArrayLike | None = None
    ) -> NDArray:
        """Compute the distance of a set of points to the nearest detector surface.

        Parameters
        ----------
        coords
            2D array of shape `(n,3)` of `(x,y,z)` coordinates for each of `n` points, second index corresponds to `(x,y,z)`.
        surface_indices
            list of indices of surfaces to consider. If `None` (the default) all surfaces used.

        Returns
        -------
        numpy array of the distance from each point to the nearest surface.

        Note
        ----
        - Only implemented for solids based on :class:`geant4.solid.GenericPolycone`
        - Coordinates should be relative to the origin of the polycone.
        """
        # check type of the solid
        if not isinstance(self.solid, geant4.solid.GenericPolycone):
            msg = f"distance_to_surface is not implemented for {type(self.solid)} yet"
            raise NotImplementedError(msg)

        if not isinstance(coords, np.ndarray):
            coords = np.array(coords)

        if np.shape(coords)[1] != 3:
            msg = "coords must be provided as a 2D array with x,y,z coordinates for each point."
            raise ValueError(msg)

        # get the coordinates
        r, z = self.get_profile()

        dists = utils.get_distance_vectors(
            coords, r, z, surface_indices=surface_indices
        )

        return np.min(abs(dists), axis=1)

    @property
    def volume(self) -> Quantity:
        """Volume of the HPGe."""
        volume = 0
        r1 = self.solid.pR[-1]
        z1 = self.solid.pZ[-1]
        for i in range(len(self.solid.pZ)):
            r2 = self.solid.pR[i]
            z2 = self.solid.pZ[i]
            volume += (r1 * r1 + r1 * r2 + r2 * r2) * (z2 - z1)
            r1 = r2
            z1 = z2

        return (2 * math.pi * abs(volume) / 6) * u.mm**3

    @property
    def mass(self) -> Quantity:
        """Mass of the HPGe."""
        return (self.volume * (self.material.density * u.g / u.cm**3)).to(u.g)

    def surface_area(self, surface_indices: list | None = None) -> Quantity:
        """Surface area of the HPGe.

        If a list of surface_indices is provided the area is computed only considering these surfaces,
        from :math:`r_i` to :math:`r_{i+1}` and :math:`z_i` to :math:`z_{i+1}`. Else the full area is computed.

        Parameters
        ----------
        surface_indices
            list of indices or None.

        Returns
        -------
        a pint Quantity of the surface area

        Note
        ----
        Calculation is based on a polycone geometry so is incorrect for asymmetric detectors.
        """
        if not isinstance(self.solid, geant4.solid.GenericPolycone):
            logging.warning("The area is that of the solid without cut")

        r, z = self.get_profile()

        r = np.array(r)
        z = np.array(z)

        dr = np.array([r2 - r1 for r1, r2 in zip(r[:-1], r[1:])])
        dz = np.array([z2 - z1 for z1, z2 in zip(z[:-1], z[1:])])
        dl = np.sqrt(np.power(dr, 2) + np.power(dz, 2))

        if surface_indices is not None:
            dr = dr[surface_indices]
            dz = dz[surface_indices]
            dl = dl[surface_indices]
            r = r[surface_indices]
            z = z[surface_indices]

        return np.sum(
            np.where(dr == 0, abs(dz) * r[:-1] * 2 * np.pi, abs(dr) * dl * np.pi)
        )
