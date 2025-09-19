# legend-pygeom-hpges

legendhpges provides High-Purity Germanium (HPGe) detector models built from
[LEGEND](https://legend-exp.org/) metadata for radiation transport simulations.
It integrates with {mod}`pyg4ometry` and [Geant4](https://geant4.web.cern.ch/)
for visualisation and simulation, and offers utilities to compute detector
properties and perform geometric queries.

## Key features

- Build detector geometry directly from human-readable input file format
- Multiple geometries supported: PPC, BEGe, Semi‑Coax, ICPC, plus special variants
- Seamless Geant4 integration via {mod}`pyg4ometry` (visualisation and GDML
  export)
- Compute volume, mass and surface areas with unit-aware quantities
- Calculation of useful geometrical queries (like distances of points to
  surfaces etc.)
- Consistent unit handling using {mod}`pint`

## Getting started

legendhpges can be installed from PyPI or conda-forge:

PyPI:

```console
$ pip install legend-pygeom-hpges
```

conda-forge:

```console
$ conda install -c conda-forge legend-pygeom-hpges
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
