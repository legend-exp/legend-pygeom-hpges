"""LEGEND HPGe material descriptions for use in geometries."""

from __future__ import annotations

from pyg4ometry import geant4

from .registry import default_registry

# TODO: enrichment argument, natural germanium


def _enriched_germanium() -> geant4.MaterialCompound:
    """Enriched Germanium builder."""
    ge70 = geant4.Isotope("Ge70", 32, 70, 69.9243)
    ge72 = geant4.Isotope("Ge72", 32, 72, 71.9221)
    ge73 = geant4.Isotope("Ge73", 32, 73, 72.9235)
    ge74 = geant4.Isotope("Ge74", 32, 74, 73.9212)
    ge76 = geant4.Isotope("Ge76", 32, 76, 75.9214)
    enrge = geant4.ElementIsotopeMixture("germanium", "Ge", 5)
    enrge.add_isotope(ge70, 0.0000397)
    enrge.add_isotope(ge72, 0.0000893)
    enrge.add_isotope(ge73, 0.000278)
    enrge.add_isotope(ge74, 0.1258)
    enrge.add_isotope(ge76, 0.8738)
    matenrge = geant4.MaterialCompound("EnrichedGermanium", 5.545, 1, default_registry)
    matenrge.add_element_massfraction(enrge, 1)
    return matenrge


enriched_germanium = _enriched_germanium()
