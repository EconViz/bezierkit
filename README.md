# bezierkit

A small mathematical toolkit for constructing and analyzing Bézier curves.

`bezierkit` is renderer-independent: it provides curve construction,
evaluation, subdivision, and sampling while leaving plotting to consumers such
as EconViz, Matplotlib, Plotly, SVG, or Typst adapters.

## Installation

Install the library only:

```bash
pip install bezierkit
```

Install the optional command-line interface:

```bash
pip install "bezierkit[cli]"
```

For development with [uv](https://docs.astral.sh/uv/):

```bash
uv sync --all-extras --dev
```

## Python API

```python
from bezierkit import BezierCurve, Point
from bezierkit.construction import PlanarSlopes
from bezierkit.sampling import UniformSampler

curve = BezierCurve.cubic(
    Point(0, 0),
    Point(1, 2),
    Point(3, 2),
    Point(4, 0),
)

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

## Command-line interface

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

The 0.2 release covers core geometry, Bézier evaluation and operations,
endpoint construction, uniform sampling, and the initial CLI. Rendering is
intentionally outside this package. Differential analysis, fitting,
piecewise curves, intersections, B-splines, and NURBS are future work.
