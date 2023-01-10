"""LEGEND HPGE material descriptions for use in geometries

Only a placeholder as it's expected that material descriptions will
eventually be obtained through a seperate, dedicated package. Originally
part of "LegendGeom" proof-of-principle package.
"""

import pyg4ometry as pg4


def enriched_germanium() -> pg4.geant4.MaterialCompound: 
    ge70 = pg4.geant4.Isotope("Ge70", 32, 70, 69.9243)
    ge72 = pg4.geant4.Isotope("Ge72", 32, 72, 71.9221)
    ge73 = pg4.geant4.Isotope("Ge73", 32, 73, 72.9235)
    ge74 = pg4.geant4.Isotope("Ge74", 32, 74, 73.9212)
    ge76 = pg4.geant4.Isotope("Ge76", 32, 76, 75.9214)
    enrge = pg4.geant4.ElementIsotopeMixture("enrichedGe", "enrGe", 5)
    enrge.add_isotope(ge70, 0.0000397)
    enrge.add_isotope(ge72, 0.0000893)
    enrge.add_isotope(ge73, 0.000278)
    enrge.add_isotope(ge74, 0.1258)
    enrge.add_isotope(ge76, 0.8738)
    matenrge = pg4.geant4.MaterialCompound("enrGe", 5.545, 1, reg)
    matenrge.add_element_massfraction(enrge, 1)
    return matenrge
