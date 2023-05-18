import pathlib

from pyg4ometry import geant4

from legendhpges import PPContact
from legendhpges.materials import enriched_germanium

configs = pathlib.Path(__file__).parent.resolve() / "config"


def test_icpc():
    reg = geant4.Registry()
    PPContact(configs / "P00662B.json", material=enriched_germanium, registry=reg)
