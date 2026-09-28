# Cubic Hermite guarantees

BezierKit uses cubic Hermite interpolation as the mathematical bridge from
functions and derivatives to directly inspectable Bézier control points.

## Parametric form

Let a smooth curve be known at parameters `t0` and `t1`, with positions
`P0`, `P3` and derivatives `D0`, `D1`. Write `h = t1 - t0` and normalize the
parameter with `s = (t - t0) / h`. The cubic controls are

```text
P1 = P0 + h D0 / 3
P2 = P3 - h D1 / 3
```

The Bézier endpoint identities give `B(0) = P0`, `B(1) = P3`,
`dB/ds(0) = 3(P1-P0) = h D0`, and
`dB/ds(1) = 3(P3-P2) = h D1`. The chain rule therefore reproduces `D0` and
`D1` with respect to the original parameter `t`. Negative `h` is valid and
reverses the parameter interval; `h = 0` is undefined and rejected.

## Graph form

For `y=f(x)`, choose `P=(x,f(x))` and `D=(1,f'(x))`. With `h=x1-x0`,

```text
P0 = (x0, y0)
P1 = (x0 + h/3, y0 + h m0/3)
P2 = (x1 - h/3, y1 - h m1/3)
P3 = (x1, y1)
```

This is exactly what `graph_hermite` implements and what
`tests/interpolation/test_hermite.py` verifies.

## Error and subdivision

For scalar cubic Hermite interpolation of a four-times differentiable
function on an interval of width `h`,

```text
max |f-H| <= |h|^4 max|f''''| / 384.
```

Halving the interval multiplies this bound by `1/16`. The helper
`hermite_error_bound` exposes the formula. Adaptive fitting additionally
measures Euclidean error at a caller-configurable number of deterministic
probe parameters. Its `tolerance` is expressed in the coordinate units of the
curve; every accepted segment exposes that measured value as `fit_error`.
Reaching `max_depth` or `max_segments` before satisfying the tolerance raises
`ToleranceNotMet`.

## Piecewise continuity

Adjacent segments are C0-continuous when the first segment's `P3` equals the
next segment's `P0` within the configured continuity tolerance. They are
C1-continuous under equal parameter spans when
`3(P3-P2) = 3(Q1-Q0)`. For unequal spans, compare derivatives after dividing
each expression by its span. `PiecewiseBezier` enforces C0; callers choose
whether C1 is appropriate for corners and kinks.

## Parameterization limits

Graph form assumes finite `dy/dx` and cannot represent a vertical tangent.
Use `parametric_hermite` instead. Implicit tracing derives a parametric tangent
`(Fy,-Fx)` from an optional gradient, so vertical tangents require no division.
At zero gradients, kinks, branches, or ambiguous cells, tracing retains an
explicit path boundary or falls back to the sampled polyline rather than
inventing an invalid slope.

Polyline and implicit fitting guarantees deviation from sampled geometry, not
from an unknown continuous source between samples. Increase contour resolution
and decrease tolerance when a stronger visual approximation is required.
