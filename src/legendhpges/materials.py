"""LEGEND HPGe material descriptions for use in geometries."""

from __future__ import annotations

from pyg4ometry import geant4

from .registry import default_g4_registry

ge70 = geant4.Isotope("Ge70", 32, 70, 69.9243)
ge72 = geant4.Isotope("Ge72", 32, 72, 71.9221)
ge73 = geant4.Isotope("Ge73", 32, 73, 72.9235)
ge74 = geant4.Isotope("Ge74", 32, 74, 73.9212)
ge76 = geant4.Isotope("Ge76", 32, 76, 75.9214)

# TODO: enrichment argument, natural germanium, cryogenic density
# TODO: decide on names


def _enriched_germanium(ge76_fraction: float = 0.92) -> geant4.MaterialCompound:
    """Enriched Germanium builder."""
    enrge = geant4.ElementIsotopeMixture(f"Germanium{ge76_fraction:.3f}", "EnrGe", 2)
    # approximation
    enrge.add_isotope(ge74, 1 - ge76_fraction)
    enrge.add_isotope(ge76, ge76_fraction)
    matenrge = geant4.MaterialCompound(
        f"EnrichedGermanium{ge76_fraction:.3f}", 5.56, 1, default_g4_registry
    )
    matenrge.add_element_massfraction(enrge, 1)
    return matenrge


enriched_germanium = _enriched_germanium()
