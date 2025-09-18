# Welcome to legendhpges's documentation!

Python package of Germanium detector geometries for radiation transport
simulations.

legendhpges provides parametrized High-Purity Germanium (HPGe) detector models
built from LEGEND metadata. It integrates with pyg4ometry/Geant4 for
visualisation and simulation, and offers utilities to compute detector
properties and perform geometric queries.

## Key features

- Build detectors directly from LEGEND metadata (YAML/JSON) or Python dicts
- Multiple geometries supported: PPC, BEGe, Semi‑Coax, ICPC, plus special variants
- Seamless Geant4 integration via pyg4ometry (visualisation and GDML export)
- Compute volume, mass and surface areas with unit-aware quantities
- Distance-to-surface and point-in-detector queries; ICPC borehole classification
- Consistent unit handling using pint

## Getting started

legendhpges can be installed with pip:

```console
$ pip install legend-pygeom-hpges
```

## Next steps

```{toctree}
:maxdepth: 1

User Manual <manual>
```

```{toctree}
:maxdepth: 1

Package API reference <api/modules>
```
