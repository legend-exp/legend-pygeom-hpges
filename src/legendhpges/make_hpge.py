from __future__ import annotations

import json

from legendmeta.jsondb import AttrsDict
from pyg4ometry import geant4

from .bege import BEGe
from .invcoax import InvertedCoax
from .materials import _enriched_germanium
from .ppc import PPC
from .registry import default_g4_registry
from .semicoax import SemiCoax


def make_hpge(
    metadata: str | dict | AttrsDict,
    registry: geant4.Registry = default_g4_registry,
    **kwargs,
) -> geant4.LogicalVolume:
    """Costructing an HPGe detector logical volume based on the detector metadata.

    Parameters
    ----------
    metadata
        LEGEND HPGe configuration metadata file containing
        detector static properties.
    registry
        pyg4ometry Geant4 registry instance.

    Other Parameters
    ----------------
    **kwargs
        Additionally, the following arguments are allowed for
        overriding the name and the material from the metadata:

        name
            name to attach to the detector. Used to name
            solid and logical volume.
        material
            pyg4ometry Geant4 material for the detector.

    Examples
    --------
        >>> gedet = make_hpge(metadata, registry)

        >>> make_hpge(metadata, registry, name = "my_det", material = my_material)

    """
    if not isinstance(metadata, (dict, AttrsDict)):
        with open(metadata) as jfile:
            gedet_meta = AttrsDict(json.load(jfile))
    else:
        gedet_meta = AttrsDict(metadata)

    kwargs.setdefault("material", _enriched_germanium(gedet_meta.production.enrichment))
    kwargs.setdefault("name", gedet_meta.name)

    if gedet_meta.type == "ppc":
        gedet = PPC(metadata, registry=registry, **kwargs)

    elif gedet_meta.type == "bege":
        gedet = BEGe(metadata, registry=registry, **kwargs)

    elif gedet_meta.type == "icpc":
        gedet = InvertedCoax(metadata, registry=registry, **kwargs)

    elif gedet_meta.type == "coax":
        gedet = SemiCoax(metadata, registry=registry, **kwargs)

    return gedet
