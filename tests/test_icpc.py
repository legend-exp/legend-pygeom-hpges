from legendhpges.icpc import icpc
from legendhpges.materials import enriched_germanium

import pathlib

def geometry_file() -> pathlib.Path:
    """Absolute path to the geometry description test file"""
    selfdir = pathlib.Path(__file__).parent.resolve()
    return selfdir.joinpath('test_icpc.py')

def test_icpc():
    """This is totally noddy just to get a placeholder"""
    detector_lv = icpc(geometry_file(), None, enriched_germanium())    
