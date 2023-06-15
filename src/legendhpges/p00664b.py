from __future__ import annotations

import math

from pyg4ometry import geant4

from .base import HPGe


class P00664B(HPGe):
    """A p-type point contact germanium detector P00664B with a special detector geometry.

    Note
    ----
        The normal vector of the cut plane is in the positive x-direction.
    """

    def _g4_solid(self):
        c = self.metadata.geometry

        # return ordered r,z lists, default unit [mm]
        r, z = self._decode_polycone_coord()

        x_cut_plane = c.extra.cut_plane.distance_from_center_in_mm

        # build generic polycone, default [mm]
        uncut_hpge = geant4.solid.GenericPolycone(
            "uncut" + self.name, 0, 2 * math.pi, r, z, self.registry
        )

        px_sliced = c.radius_in_mm - x_cut_plane
        py_sliced = 2 * c.radius_in_mm

        cut_plane = geant4.solid.Box(
            "cut_plane_" + self.name,
            px_sliced,
            py_sliced,
            c.height_in_mm,
            self.registry,
        )

        g4_solid = geant4.solid.Subtraction(
            self.name,
            uncut_hpge,
            cut_plane,
            [[0, 0, 0], [x_cut_plane + px_sliced / 2, 0, c.height_in_mm / 2]],
            self.registry,
        )

        return g4_solid

    def _decode_polycone_coord(self):
        c = self.metadata.geometry

        def _tan(a):
            return math.tan(math.pi * a / 180)

        r = []
        z = []

        if c.pp_contact.depth_in_mm > 0:
            r += [0, c.pp_contact.radius_in_mm, c.pp_contact.radius_in_mm]
            z += [c.pp_contact.depth_in_mm, c.pp_contact.depth_in_mm, 0]
        else:
            r += [0]
            z += [0]

        if c.taper.bottom.height_in_mm > 0:
            r += [
                c.radius_in_mm
                - c.taper.bottom.height_in_mm * _tan(c.taper.bottom.angle_in_deg),
                c.radius_in_mm,
            ]
            z += [0, c.taper.bottom.height_in_mm]
        else:
            r += [c.radius_in_mm]
            z += [0]

        if c.taper.top.height_in_mm > 0:
            r += [
                c.radius_in_mm,
                c.radius_in_mm
                - c.taper.top.height_in_mm * _tan(c.taper.top.angle_in_deg),
            ]
            z += [c.height_in_mm - c.taper.top.height_in_mm, c.height_in_mm]
        else:
            r += [c.radius_in_mm]
            z += [c.height_in_mm]

        r += [0]
        z += [c.height_in_mm]

        return r, z
