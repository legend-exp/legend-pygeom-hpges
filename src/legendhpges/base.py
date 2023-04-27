from __future__ import annotations

import json
import math
from abc import ABC, abstractmethod

from legendmeta.jsondb import AttrsDict
from pyg4ometry import geant4

from .materials import enriched_germanium
from .registry import default_registry


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
        name: str = None,
        registry: geant4.Registry = default_registry,
        material: geant4.MaterialCompound = enriched_germanium,
    ) -> None:
        if registry is None:
            raise ValueError("registry cannot be None")

        if metadata is None:
            raise ValueError("metadata cannot be None")

        # build crystal, declare as detector
        if not isinstance(metadata, (dict, AttrsDict)):
            with open(metadata) as jfile:
                self.metadata = AttrsDict(json.load(jfile))
        else:
            self.metadata = AttrsDict(metadata)

        if name is None:
            self.name = self.metadata.name

        # return ordered r,z lists, default unit [mm]
        r, z = self._decode_polycone_coord()

        # build generic polycone, and logical volume, default [mm]
        ic_solid = geant4.solid.GenericPolycone(
            self.name, 0, 2 * math.pi, r, z, registry
        )

        super().__init__(ic_solid, material, self.name, registry)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.metadata})"

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
        pass
