import pathlib

from pyg4ometry import geant4

from legendhpges import SemiCoax
from legendhpges.materials import enriched_germanium

configs = pathlib.Path(__file__).parent.resolve() / "config"


def test_sc():
    reg = geant4.Registry()
    SemiCoax(configs / "C00ANG2.json", material=enriched_germanium, registry=reg)
