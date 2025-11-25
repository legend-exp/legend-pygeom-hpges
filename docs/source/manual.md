# Basic User Manual

This package implements an HPGe (high purity germanium detector) class which
describes the detector geometry, and can be used for:

- visualisation with [pyg4ometry](https://pyg4ometry.readthedocs.io/en/stable/)
- exporting to GDML for Geant4 simulations (again with pyg4ometry)
- computing detector properties

:::{tip}
All linear dimensions in the geometry are expressed in millimetres (mm). Returned
areas, volumes and masses are {mod}`pint` quantities and can be converted to other units.
:::

## Metadata specification

The detector geometry is constructed based on the
[LEGEND metadata specification](https://legend-exp.github.io/legend-data-format-specs/dev/metadata/).
The
[LEGEND HPGe detector metadata database](https://github.com/legend-exp/legend-detectors/tree/main/germanium/diodes)
is **private**.

The metadata YAML files (or Python dictionaries) describe the geometry (and
other properties) for detectors:

```python
metadata = {
    "name": "B00000B",
    "type": "bege",
    "production": {
        "enrichment": {"val": 0.9, "unc": 0.003},
        "mass_in_g": 697.0,
    },
    "geometry": {
        "height_in_mm": 29.46,
        "radius_in_mm": 36.98,
        "groove": {"depth_in_mm": 2.0, "radius_in_mm": {"outer": 10.5, "inner": 7.5}},
        "pp_contact": {"radius_in_mm": 7.5, "depth_in_mm": 0},
        "taper": {
            "top": {"angle_in_deg": 0.0, "height_in_mm": 0.0},
            "bottom": {"angle_in_deg": 0.0, "height_in_mm": 0.0},
        },
    },
}
```

:::{note}
Currently BEGe, ICPC, PPC and Coax geometries are implemented as well
as a few LEGEND detectors with special geometries. Different geometries can be
implemented as subclasses deriving from {class}`~.base.HPGe`.
:::

The different keys of the dictionary describe the different aspects of the
geometry. Some are self explanatory, for others:

- `production`: gives information on the detector production, we need the
  "enrichment" to define the detector material,
- `geometry` : gives the detector geometry in particular, `groove` and
  `pp_contact` describe the contacts of detector.
- Optional `extra` sections enable special features (e.g. cracks, top grooves, bottom
  cylinders) for specific detector types.

Other fields can be added to describe different geometry features (more details
in the legend metadata documentation).

### Supported geometries

- PPC: {class}`~.ppc.PPC`
- BEGe: {class}`~.bege.BEGe`
- Semi-coax: {class}`~.semicoax.SemiCoax`
- ICPC (inverted coax): {class}`~.invcoax.InvertedCoax`
- Special asymmetrical variants of other detector types, as found in LEGEND:
  {class}`~.p00664b.P00664B`, {class}`~.v02160a.V02160A`, {class}`~.v07646a.V07646A`,
  {class}`~.v02162b.V02162B`

## Constructing the HPGe object

The HPGe object can be constructed from the metadata with:

```pycon
>>> from pygeomhpges import make_hpge
>>> import pyg4ometry as pg4
>>> reg = pg4.geant4.Registry()
>>> hpge = make_hpge(metadata, name="det_L", registry=reg)
>>> hpge  # doctest: +SKIP
BEGe({...})
```

The metadata can either be passed as a Python dictionary or a path to a
YAML/JSON file:

```pycon
>>> hpge = make_hpge("path/to/metadata.yaml", registry=reg)  # doctest: +SKIP
```

:::{important}
If the `production.enrichment` field is present in the metadata, the material is
automatically set to enriched germanium with the corresponding $^{76}$Ge fraction
(approximated as a 74/76 mixture). If you pass your own `material` argument,
it must belong to the same Geant4 registry you pass in.
:::

### Handling asymmetries

For detectors that break cylindrical symmetry (e.g. {class}`~.v02160a.V02160A`,
{class}`~.p00664b.P00664B`), {func}`.make_hpge` will build special subclasses if
`allow_cylindrical_asymmetry=True` (default). Set it to `False` to get a
symmetrized {class}`~.invcoax.InvertedCoax` or {class}`~.ppc.PPC` shape:

```pycon
>>> hpge_sym = make_hpge(
...     metadata, registry=reg, allow_cylindrical_asymmetry=False
... )  # doctest: +SKIP
```

## Detector properties

Most detectors are described by a
{class}`G4GenericPolycone <pyg4ometry.geant4.solid.GenericPolycone>`. This
describes the solid by a series of $(r,z)$ pairs rotated around the $z$ axis.

There are methods to plot the $(r,z)$ profile of the detector, in addition this
is able to label the contact type (p+, n+ or passivated) each surface
corresponds to (based on the metadata).

```python
from pygeomhpges import draw

draw.plot_profile(hpge, split_by_type=True)
```

```{image} images/bege_profile.png
:width: 70%
:align: center
```

We can also directly extract the $(r,z)$ profile and the surface types and
surface area of each.

```pycon
>>> r, z = hpge.get_profile()
>>> hpge.surfaces
['pplus', 'passive', 'passive', 'passive', 'nplus', 'nplus', 'nplus']
>>> sum(hpge.surface_area())
<Quantity(13775.3258, 'millimeter ** 2')>
>>> hpge.surface_area(hpge.surfaces.index("nplus"))
<Quantity(2202.8546..., 'millimeter ** 2')>
```

Here the surfaces correspond to the line from $r_i$ to $r_{i+1}$ and $z_i$ to
$z_{i+1}$.

We can also easily extract the detector mass and volume:

```pycon
>>> hpge.mass
<Quantity(700.577026, 'gram')>
>>> hpge.volume
<Quantity(126226.526, 'millimeter ** 3')>
>>> # Convert to cm^3 if desired:
>>> hpge.volume.to("cm**3")
<Quantity(126.226526, 'centimeter ** 3')>
```

### Distances and containment

Compute the shortest distance of points to the closest detector surface:

```pycon
>>> # shape (N, 3), columns are x, y, z in mm
>>> hpge.distance_to_surface([(0, 0, 1), (0, 0, 99)])
array([ 1.  , 69.54])
```

Check whether points are inside:

```pycon
>>> hpge.is_inside([(0, 0, 1), (0, 0, 99)])
array([ True, False])
```

Distances are computed in $(r,z)$ after converting from $(x,y,z)$. A tolerance
`tol` is used to treat points very close to the surface as inside.

:::{note}

For asymmetric detectors implemented via CSG subtraction (e.g. {class}`~.v02160a.V02160A`,
{class}`~.p00664b.P00664B`), `get_profile()` returns the uncut polycone profile.
Consequently, `surface_area()` refers to the symmetric parent polycone.

:::

### ICPC borehole classification

For ICPC-based detectors, you can test if points are inside the borehole:

```pycon
>>> from pygeomhpges import InvertedCoax
>>> isinstance(hpge, InvertedCoax)
True
>>> hpge.is_inside_borehole([(0, 0, hpge.metadata.geometry.height_in_mm - 1)])
array([False])
```

## Materials

Two convenience builders are provided:

- {func}`.materials.make_natural_germanium`
- {func}`.materials.make_enriched_germanium`

{func}`.make_hpge` selects the material automatically from metadata if
`production.enrichment` is provided; otherwise natural germanium is used.

```pycon
>>> from pygeomhpges.materials import make_enriched_germanium
>>> mat = make_enriched_germanium(0.92, registry=reg)  # doctest: +SKIP
```

## Visualisation and Geant4 usage

The HPGe object derives from {class}`pyg4ometry.geant4.LogicalVolume` and can be
used to visualise the detector in 3D, or to run Geant4 simulations.

For example to visualise a detector we can use:

```python
import pyg4ometry as pg4

# create a world volume
world_s = pg4.geant4.solid.Orb("World_s", 20, registry=reg, lunit="cm")
world_l = pg4.geant4.LogicalVolume(world_s, "G4_Galactic", "World", registry=reg)
reg.setWorld(world_l)

# place the detector
pg4.geant4.PhysicalVolume(
    [0, 0, 0], [0, 0, 0, "cm"], hpge, "det", world_l, registry=reg
)

viewer = pg4.visualisation.VtkViewerColoured()
viewer.addLogicalVolume(reg.getWorldVolume())
viewer.view()
```

```{image} images/bege.png
:width: 70%
:align: center
```

The [remage tutorial](https://remage.readthedocs.io/en/stable/) gives a more
complete example of using pygeomhpges to run a simulation.

## Tips and troubleshooting

- Ensure coordinate arrays are shape `(N, 3)` in `(x, y, z)` with units of mm.
- A {class}`NotImplementedError` is raised by distance methods for solids that
  are not {class}`pyg4ometry.geant4.solid.GenericPolycone`.

## Extending

New detector variants can be added by subclassing {class}`~.base.HPGe` and
implementing {meth}`.base.HPGe._decode_polycone_coord`. For asymmetric shapes,
override {meth}`.base.HPGe._g4_solid` to build a CSG subtracted solid.

This package is also used in the [_legend-pygeom-l200_ implementation of the
LEGEND-200 experiment](https://github.com/legend-exp/legend-pygeom-l200).
