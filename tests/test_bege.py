import pathlib

from pyg4ometry import geant4

from legendhpges import BEGe
from legendhpges.materials import enriched_germanium

configs = pathlib.Path(__file__).parent.resolve() / "config"


def test_bege():
    reg = geant4.Registry()
    BEGe(configs / "B00091A.json", material=enriched_germanium, registry=reg)
