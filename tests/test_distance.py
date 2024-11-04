from __future__ import annotations

import pathlib

import numpy as np
import pytest
from legendmeta import TextDB
from legendtestdata import LegendTestData
from pyg4ometry import geant4

from legendhpges import (
    make_hpge,
)
from legendhpges.materials import make_natural_germanium

reg = geant4.Registry()
natural_germanium = make_natural_germanium(reg)
configs = TextDB(pathlib.Path(__file__).parent.resolve() / "configs")


@pytest.fixture(scope="session")
def test_data_configs():
    ldata = LegendTestData()
    ldata.checkout("2553a28")
    return ldata.get_path("legend/metadata/hardware/detectors/germanium/diodes")


def test_not_implemented():
    reg = geant4.Registry()
    ppc = make_hpge(configs.P00664B, registry=reg)

    with pytest.raises(NotImplementedError):
        ppc.distance_to_surface([[1, 0, 0]])


def test_bad_dimensions(test_data_configs):
    reg = geant4.Registry()
    gedet = make_hpge(test_data_configs + "/C99000A.json", registry=reg)

    with pytest.raises(ValueError):
        gedet.distance_to_surface([[1, 0, 0, 0]])


def test_output(test_data_configs):
    reg = geant4.Registry()
    gedet = make_hpge(test_data_configs + "/C99000A.json", registry=reg)
    dist = gedet.distance_to_surface([[0, 0, 0], [1, 3, 3], [0, 0, 0]])

    assert np.shape(dist == (3,))
    assert np.all(dist >= 0)

    dist_indices = gedet.distance_to_surface(
        [[0, 0, 0], [1, 3, 3], [0, 0, 0]], surface_indices=[0, 3]
    )
    assert np.all(dist_indices >= dist)



def test_inside_not_implemented():
    reg = geant4.Registry()
    ppc = make_hpge(configs.P00664B, registry=reg)

    with pytest.raises(NotImplementedError):
        ppc.is_inside([[1, 0, 0]])

def test_inside_bad_dimensions(test_data_configs):
    reg = geant4.Registry()
    gedet = make_hpge(test_data_configs + "/C99000A.json", registry=reg)

    with pytest.raises(ValueError):
        gedet.is_inside([[1, 0, 0, 0]])


def test_output(test_data_configs):
    reg = geant4.Registry()
    print(test_data_configs + "/B99000A.json")
    gedet = make_hpge(test_data_configs + "/B99000A.json", registry=reg)
    r,z = gedet._decode_polycone_coord()
    print(r,z)
    # detetor is a simple bege
    # groove at 7.5-12 mm
    is_in= gedet.is_inside([[0, 0, 0], [1, 3, 3], [0, 0, 0]])

    assert np.shape(is_in== (3,))
