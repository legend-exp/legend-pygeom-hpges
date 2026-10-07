from __future__ import annotations

import math

from .base import HPGe
from .build_utils import make_pplus


class V06649(HPGe):
    """An inverted-coaxial point contact germanium detector V06649A/M with a special geometry."""

    def _decode_polycone_coord(self) -> tuple[list[float], list[float]]:
        c = self.metadata.geometry

        def _tan(a):
            return math.tan(math.pi * a / 180)

        r = []
        z = []
        surfaces = []

        # save the borehole coords
        borehole_r = []
        borehole_z = []

        r_p, z_p, surface_p = make_pplus(c)
        r += r_p
        z += z_p
        surfaces += surface_p

        if c.taper.bottom.height_in_mm > 0:
            r += [
                c.radius_in_mm
                - c.taper.bottom.height_in_mm * _tan(c.taper.bottom.angle_in_deg),
                c.radius_in_mm,
            ]

            z += [
                0,
                c.taper.bottom.height_in_mm,
            ]
            surfaces += ["nplus", "nplus"]

        else:
            r += [c.radius_in_mm]
            z += [0]
            surfaces += ["nplus"]

        # the top of the crystal is a narrower cylinder; the top taper bevels
        # the outer edge of its top face
        if c.extra.top_cylinder.height_in_mm > 0:
            r_top = c.extra.top_cylinder.radius_in_mm
            r += [c.radius_in_mm, r_top]
            z += [c.height_in_mm - c.extra.top_cylinder.height_in_mm] * 2
            surfaces += ["nplus", "nplus"]
        else:
            r_top = c.radius_in_mm

        if c.taper.top.height_in_mm > 0:
            r += [
                r_top,
                r_top - c.taper.top.height_in_mm * _tan(c.taper.top.angle_in_deg),
            ]
            z += [c.height_in_mm - c.taper.top.height_in_mm, c.height_in_mm]
            surfaces += ["nplus", "nplus"]
        else:
            r += [r_top]
            z += [c.height_in_mm]
            surfaces += ["nplus"]

        # first point of the borehole
        borehole_r += [0]
        borehole_z += [c.height_in_mm]

        if c.taper.borehole.height_in_mm > 0:
            r += [
                c.borehole.radius_in_mm
                + c.taper.borehole.height_in_mm * _tan(c.taper.borehole.angle_in_deg),
                c.borehole.radius_in_mm,
            ]

            z += [
                c.height_in_mm,
                c.height_in_mm - c.taper.borehole.height_in_mm,
            ]
            surfaces += ["nplus", "nplus"]

            # add borehole coords
            borehole_r += r[-2:]
            borehole_z += z[-2:]
        else:
            r += [c.borehole.radius_in_mm]
            z += [c.height_in_mm]
            surfaces += ["nplus"]

            borehole_r += [r[-1]]
            borehole_z += [z[-1]]

        # add borehole with or without tapering
        if c.taper.borehole.height_in_mm != c.borehole.depth_in_mm:
            r += [
                c.borehole.radius_in_mm,
                0,
            ]

            z += [
                c.height_in_mm - c.borehole.depth_in_mm,
                c.height_in_mm - c.borehole.depth_in_mm,
            ]
            surfaces += ["nplus", "nplus"]

            borehole_r += r[-2:]
            borehole_z += z[-2:]

        else:
            r += [0]

            z += [c.height_in_mm - c.borehole.depth_in_mm]
            surfaces += ["nplus"]

            borehole_r += [r[-1]]
            borehole_z += [z[-1]]

        self.surfaces = surfaces

        # save the borehole coordinates for future reference

        # reverse to keep clockwise orientation
        self.borehole_r = borehole_r[::-1]
        self.borehole_z = borehole_z[::-1]

        return r, z
