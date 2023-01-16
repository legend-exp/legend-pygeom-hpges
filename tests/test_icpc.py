import pathlib

from legendhpges.icpc import ICPC
from legendhpges.materials import enriched_germanium


def geometry_file() -> pathlib.Path:
    """Absolute path to the geometry description test file."""
    selfdir = pathlib.Path(__file__).parent.resolve()
    return selfdir.joinpath("test_icpc.py")


def test_icpc():
    """Noddy check just to put a placeholder down."""
    detector_lv = ICPC(geometry_file(), None, enriched_germanium())
