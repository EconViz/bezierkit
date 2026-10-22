# Changelog

All notable changes to this project are documented in this file. The project
follows [semantic versioning](https://semver.org/) from 1.0.0.

## Unreleased

### Added

- `bezierkit.implicit.trace_sampled(xs, ys, values, *, levels, ...)` traces
  level sets of a field that has already been sampled on a grid. A caller that
  can evaluate the whole grid in one vectorized call skips the one Python call
  per grid point that `trace_implicit` makes.

### Changed

- Faster contour tracing with the same results. Marching squares, the Ramer-Douglas-Peucker
  simplification in `fit_polyline`, its fit error, `PiecewiseBezier.at_many` and the endpoint keys
  of the stitching step now work on arrays instead of one point at a time. The kernels apply the
  same formulas in the same order as before, so the traced paths and control points are unchanged
  in every test, and 14 figures rendered through utility-viz are byte-identical on macOS (ARM) and
  on Linux (ARM and x86-64). A batched `norm` can differ from the scalar one in the last bit, so a
  `fit_error` may differ by about 1e-16 (observed on x86-64: 1.1e-16 where exactly collinear points
  gave 0.0). On the utility-viz indifference-map figures the traced figures render about 4x faster,
  with the grid evaluation still done per point.

## 1.0.1 (2026-10-04)

### Fixed

- The PyPI project description now shows the README banner: it is loaded
  from an absolute URL instead of the repository-relative
  `docs/assets/banner.svg`, which PyPI cannot resolve. No code changes.

## 1.0.0 (2026-10-04)

First stable release. The public API is everything exported from `bezierkit`
and its documented subpackages (`bezier`, `construction`, `interpolation`,
`fitting`, `implicit`, `sampling`, `export`, `adapters.matplotlib`); it follows
semantic versioning from this release. The JSON path schema remains version 1.

### Fixed

- `PiecewiseBezier.segment(t0, t1)` returned the wrong end point whenever `t0`
  fell inside a segment: it re-split the already split path, whose uniform
  parameterization differs from the original's. Both ends are now located in
  the original path, an end on a segment boundary adds no degenerate piece,
  and closed paths are rejected as `split()` already rejects them.

### Changed

- Development status is now "Production/Stable".

## 0.5.0rc1 (2026-09-28)

First release on PyPI, combining the 0.2-0.5 development milestones.

- Degree- and dimension-generic `BezierCurve` with de Casteljau (default) and
  Bernstein evaluators, hodographs, subdivision, segment extraction and
  reversal; immutable `Point`, `Vector`, `PointSet`, `Interval` and
  `ParameterValues`.
- `CubicBezierSegment` with tight bounding boxes, exact degree elevation of
  lines and quadratics (`to_cubic`), and `PiecewiseBezier` paths with closure
  metadata and compound subpaths.
- Endpoint constructions (`EndpointDerivatives`, `TangentDirections`,
  `PlanarSlopes`) and cubic Hermite interpolation (`parametric_hermite`,
  `graph_hermite`).
- Adaptive fitting with measured error (`fit_parametric`, `fit_graph`,
  `hermite_error_bound`), polyline simplification (`fit_polyline`) and
  marching-squares level-set tracing (`trace_implicit`).
- Uniform sampling, the versioned JSON path schema, SVG path data and native
  TikZ export, optional Matplotlib `Path` interoperability, and the
  `bezierkit` command-line interface (`evaluate`, `sample`, `construct`).
