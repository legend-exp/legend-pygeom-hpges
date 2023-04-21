from __future__ import annotations

import json
from math import pi, tan

from legendmeta.jsondb import AttrsDict
from pyg4ometry import geant4

from .base import HPGe
from .materials import enriched_germanium
from .registry import default_registry


class InvertedCoax(HPGe):
    """An inverted-coaxial point contact germanium detector.

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
        if not isinstance(metadata, dict | AttrsDict):
            with open(metadata) as jfile:
                self.metadata = AttrsDict(json.load(jfile))
        else:
            self.metadata = AttrsDict(metadata)

        if name is None:
            self.name = self.metadata.name

        # return ordered r,z lists, default unit [mm]
        r, z = _decode_polycone_coord(self.metadata.geometry)

        # build generic polycone, and logical volume, default [mm]
        ic_solid = geant4.solid.GenericPolycone(self.name, 0, 2 * pi, r, z, registry)
        self.logical_volume = geant4.LogicalVolume(
            ic_solid, material, self.name, registry
        )

    def __repr__(self) -> str:
        return f"InvertedCoax({self.metadata})"


def _decode_polycone_coord(metadata) -> tuple[list[float], list[float]]:
    """Decode shape information from geometry dictionary into (r, z) coordinates.

    Suitable for building a :class:`G4GenericPolycone`.

    Parameters
    ----------
    config
        dictionary extracted from JSON file, containing crystal shape
        information.

    Returns
    -------
    (list1, list2)
        2 lists of r and z coordinates, respectively.

    """
    c = metadata

    def _tan(a):
        return tan(180 * a / pi)

    r = [
        0,
        c.groove.radius_in_mm.inner,
        c.groove.radius_in_mm.inner,
        c.groove.radius_in_mm.outer,
        c.groove.radius_in_mm.outer,
        c.radius_in_mm
        - c.taper.bottom.height_in_mm * _tan(c.taper.bottom.angle_in_deg),
        c.radius_in_mm,
        c.radius_in_mm,
        c.radius_in_mm - c.taper.top.height_in_mm * _tan(c.taper.top.angle_in_deg),
        c.borehole.radius_in_mm
        + c.taper.borehole.height_in_mm * _tan(c.taper.borehole.angle_in_deg),
        c.borehole.radius_in_mm,
        c.borehole.radius_in_mm,
        0,
    ]
    z = [
        0,
        0,
        c.groove.depth_in_mm,
        c.groove.depth_in_mm,
        0,
        0,
        c.taper.bottom.height_in_mm,
        c.height_in_mm - c.taper.top.height_in_mm,
        c.height_in_mm - c.taper.top.height_in_mm,
        c.height_in_mm - c.taper.borehole.height_in_mm,
        c.height_in_mm - c.borehole.depth_in_mm,
        c.height_in_mm - c.borehole.depth_in_mm,
    ]

    return r, z
