from __future__ import annotations

import sys
import warnings

import pygeomhpges  # noqa: F401

sys.modules[__name__] = sys.modules["pygeomhpges"]

warnings.warn(
    "Please use `pygeomhpges` instead of `legendhpges`.", FutureWarning, stacklevel=2
)
