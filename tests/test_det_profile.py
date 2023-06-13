import pathlib

import pytest
from legendtestdata import LegendTestData
from pyg4ometry import geant4

from legendhpges import PPC, V07646A, BEGe, InvertedCoax, SemiCoax, make_hpge
from legendhpges.materials import enriched_germanium

reg = geant4.Registry()
configs = pathlib.Path(__file__).parent.resolve() / "configs"


@pytest.fixture(scope="session")
def test_data_configs():
    ldata = LegendTestData()
    ldata.checkout("5f9b368")
    configs = ldata.get_path("legend/metadata/hardware/detectors/germanium/diodes")
    return configs


def test_icpc(test_data_configs):
    InvertedCoax(
        test_data_configs + "/V99000A.json", material=enriched_germanium, registry=reg
    )


def test_bege(test_data_configs):
    BEGe(test_data_configs + "/B99000A.json", material=enriched_germanium, registry=reg)


def test_ppc(test_data_configs):
    PPC(test_data_configs + "/P99000A.json", material=enriched_germanium, registry=reg)


def test_semicoax(test_data_configs):
    SemiCoax(
        test_data_configs + "/C99000A.json", material=enriched_germanium, registry=reg
    )


def test_v07646a():
    V07646A(configs / "V07646A.json", material=enriched_germanium, registry=reg)


def test_make_icpc(test_data_configs):
    gedet = make_hpge(test_data_configs + "/V99000A.json")
    assert isinstance(gedet, InvertedCoax)


def test_make_bege(test_data_configs):
    gedet = make_hpge(test_data_configs + "/B99000A.json")
    assert isinstance(gedet, BEGe)


def test_make_ppc(test_data_configs):
    gedet = make_hpge(test_data_configs + "/P99000A.json")
    assert isinstance(gedet, PPC)


def test_make_semicoax(test_data_configs):
    gedet = make_hpge(test_data_configs + "/C99000A.json")
    assert isinstance(gedet, SemiCoax)


def make_v07646a():
    gedet = make_hpge(configs / "V07646A.json")
    assert isinstance(gedet, V07646A)
