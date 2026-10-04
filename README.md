# bezierkit

<p align="center">
  <img src="docs/assets/banner.svg" alt="bezierkit" width="480">
</p>

<p align="center">
  <a href="https://pypi.org/project/bezierkit/"><img alt="PyPI" src="https://img.shields.io/pypi/v/bezierkit?style=flat-square&color=181818&labelColor=f3f3f3&cacheSeconds=300"></a>
  <a href="https://pypi.org/project/bezierkit/"><img alt="Python" src="https://img.shields.io/pypi/pyversions/bezierkit?style=flat-square&color=181818&labelColor=f3f3f3"></a>
  <a href="https://opensource.org/licenses/MIT"><img alt="License" src="https://img.shields.io/badge/License-MIT-181818?style=flat-square&color=181818&labelColor=f3f3f3"></a>
  <img alt="Tests" src="https://img.shields.io/badge/tests-184%20passed-181818?style=flat-square&color=181818&labelColor=f3f3f3">
</p>

A small mathematical toolkit for constructing and analyzing Bézier curves.

`bezierkit` is renderer-independent: it provides curve construction,
evaluation, subdivision, and sampling while leaving plotting to consumers such
as EconViz, Matplotlib, Plotly, SVG, or Typst adapters.

## Installation

Add the library to your project with [uv](https://docs.astral.sh/uv/):

```bash
uv add bezierkit
```

Add the optional command-line interface:

```bash
uv add "bezierkit[cli]"
```

For development, clone the repo and sync all extras:

```bash
uv sync --all-extras --dev
```

Run anything inside the environment with `uv run`, e.g. `uv run pytest` or
`uv run bezierkit --help`. A plain `pip install bezierkit` /
`pip install "bezierkit[cli]"` also works if you are not using uv.

## Python API

```python
from bezierkit import BezierCurve, CubicBezierSegment, PiecewiseBezier, Point
from bezierkit.construction import PlanarSlopes
from bezierkit.sampling import UniformSampler

curve = BezierCurve.cubic(
    Point(0, 0),
    Point(1, 2),
    Point(3, 2),
    Point(4, 0),
)

segment = CubicBezierSegment(
    Point(0, 0),
    Point(1, 2),
    Point(3, 2),
    Point(4, 0),
)
segment.control_points        # (P0, P1, P2, P3)

path = PiecewiseBezier([
    CubicBezierSegment.from_line(Point(0, 0), Point(2, 0)),
    CubicBezierSegment.from_line(Point(2, 0), Point(2, 4)),
])
path.at(0.75)                 # Point(2.0, 2.0)

curve.at(0.5)                 # Point(2.0, 1.5)
curve.derivative().at(0.5)    # first derivative
left, right = curve.split(0.3)
sample = UniformSampler(200).sample(curve)

demand = PlanarSlopes(
    start=Point(0, 5),
    end=Point(5, 0),
    start_slope=-2,
    end_slope=-0.3,
).build()
```

The engine supports arbitrary degree and dimension. `Point`, `Vector`,
`PointSet`, control polygons, and sampling results are immutable value objects.

`CubicBezierSegment` is the primary renderer-facing value object. It exposes
`p0`, `p1`, `p2`, `p3`, tight axis-aligned bounds, and cubic-preserving split
and reversal operations. Existing `BezierCurve.cubic(...)` code remains valid;
use `CubicBezierSegment.from_curve(curve)` to migrate without changing any
control point, or `segment.as_curve()` when a degree-generic API is required.

`PiecewiseBezier` divides `[0, 1]` uniformly across the segments of a single
subpath. Closure is metadata and never inserts a hidden closing segment.
`PiecewiseBezier.compound(...)` preserves independent subpaths for fills and
holes; evaluate and split each subpath independently because a compound path
has no single continuous parameterization. Reversal preserves each subpath;
splitting is defined only for a single open subpath.

Linear and quadratic inputs can be elevated without changing their geometry:

```python
from bezierkit.bezier import to_cubic

cubic = to_cubic(BezierCurve.quadratic(
    Point(0, 0), Point(3, 6), Point(9, 0)
))
```

Batch evaluation uses a vectorized de Casteljau implementation by default.
`BernsteinEvaluator` is also available from `bezierkit.bezier.evaluation` for
explicit low-degree throughput tradeoffs; see `benchmarks/` for the
reproducible 400, 10,000, and 100,000-value benchmark.

## Interpolation, fitting, and level sets

```python
from bezierkit.fitting import fit_graph
from bezierkit.implicit import trace_implicit
from bezierkit.interpolation import graph_hermite

segment = graph_hermite(
    x0=1, x1=1.5,
    y0=4, y1=8 / 3,
    m0=-8, m1=-32 / 9,
)

path = fit_graph(
    lambda x: 4 / x**2,
    lambda x: -8 / x**3,
    x0=0.8, x1=3,
    tolerance=1e-3,
)

contours = trace_implicit(
    lambda x, y: x**2 * y,
    levels=[1, 2, 4],
    viewport=(0.5, 4, 0, 6),
    resolution=(121, 121),
    tolerance=0.01,
    gradient=lambda x, y: (2 * x * y, x**2),
)
```

Adaptive fitting reports a measured Euclidean error on every segment and
raises `ToleranceNotMet` if configured limits prevent the requested tolerance.
Implicit tracing preserves disconnected and closed components as independent
paths and uses parametric gradient tangents, including at vertical tangencies.
The derivations, error bound, continuity conditions, and sampling limitations
are documented in `docs/math/interpolation.md`.

## Exporters and adapters

```python
from bezierkit.export.json import dumps, loads
from bezierkit.export.svg import to_svg_path_data
from bezierkit.export.tikz import to_tikz

json_document = dumps(path, metadata={"name": "indifference-curve"})
same_path = loads(json_document).path
svg_path_data = to_svg_path_data(path, precision=5)
tikz = to_tikz(path, precision=5, options="thick")
```

TikZ uses native `.. controls ... and ... ..` commands and SVG uses native
`C` commands; neither exporter flattens cubic geometry or chooses a theme.
The versioned JSON schema preserves all controls, subpaths, closure, dimension,
and caller metadata.

Matplotlib interoperability is optional:

```bash
uv add "bezierkit[matplotlib]"
```

```python
from bezierkit.adapters.matplotlib import from_path, to_path

geometry = from_path(matplotlib_path, transform=affine_transform)
round_trip = to_path(geometry)
```

Affine transforms preserve controls exactly. Non-affine transforms require
the explicit `approximate_path(..., tolerance=...)` API. Format guarantees and
round-trip tolerances are documented in `docs/exporters.md`.

## Command-line interface

Run `bezierkit` directly if it's installed in your active environment, or
prefix every command with `uv run` (e.g. `uv run bezierkit --help`) when
working inside a uv project without activating the venv.

Evaluate a curve or derivative:

```bash
bezierkit evaluate \
  --points "0,0" --points "1,2" --points "3,2" --points "4,0" \
  --t 0:1:0.25 --order 1 --json
```

Sample as CSV:

```bash
bezierkit sample \
  --points "0,0" --points "1,2" --points "3,2" --points "4,0" \
  --count 50 --format csv > curve.csv
```

Construct a curve from planar slopes and pipe its control points directly into
another command:

```bash
bezierkit construct slopes \
  --start "0,5" --end "5,0" \
  --start-slope -2 --end-slope -0.3 \
| bezierkit sample --count 20 --format json
```

Run `bezierkit --help` for the complete command tree. Expected domain and input
errors are printed without a traceback; add the global `--debug` option before
the subcommand when diagnosing unexpected failures.

## Scope

Version 1.0 is the first stable release: the public API listed in
`bezierkit.__all__` and the subpackages documented above follow semantic
versioning from here on, and the JSON path schema stays at version 1. See
[CHANGELOG.md](CHANGELOG.md) for the release history. Rendering style and
diagram semantics remain intentionally outside this package. Intersections, B-splines,
and NURBS are future work.
