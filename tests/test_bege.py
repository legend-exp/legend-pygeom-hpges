import pathlib

from pyg4ometry import geant4

from legendhpges import BroadEnergy
from legendhpges.materials import enriched_germanium

configs = pathlib.Path(__file__).parent.resolve() / "config"


def test_icpc():
    reg = geant4.Registry()
    BroadEnergy(configs / "B00091A.json", material=enriched_germanium, registry=reg)
