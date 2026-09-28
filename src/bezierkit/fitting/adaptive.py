from __future__ import annotations

import math
from collections.abc import Callable

import numpy as np

from bezierkit.bezier.path import PiecewiseBezier
from bezierkit.bezier.segment import CubicBezierSegment
from bezierkit.core.errors import ToleranceNotMet
from bezierkit.core.geometry.point import Point
from bezierkit.core.geometry.vector import Vector
from bezierkit.interpolation.hermite import parametric_hermite

ParametricFunction = Callable[[float], Point]
DerivativeFunction = Callable[[float], Vector]


def hermite_error_bound(max_fourth_derivative: float, t0: float, t1: float) -> float:
    """Return the cubic Hermite sup-norm bound ``M |h|^4 / 384``."""
    maximum = float(max_fourth_derivative)
    if not math.isfinite(maximum) or maximum < 0.0:
        raise ValueError("max_fourth_derivative must be finite and non-negative")
    return maximum * abs(float(t1) - float(t0)) ** 4 / 384.0


def _measured_error(
    function: ParametricFunction,
    segment: CubicBezierSegment,
    start: float,
    end: float,
    samples: int,
) -> float:
    parameters = np.linspace(start, end, samples)
    normalized = np.linspace(0.0, 1.0, samples)
    expected = np.asarray([function(float(value)).coords for value in parameters])
    actual = segment.at_many(normalized).array
    return float(np.linalg.norm(expected - actual, axis=1).max())


def fit_parametric(
    function: ParametricFunction,
    derivative: DerivativeFunction,
    *,
    t0: float,
    t1: float,
    tolerance: float,
    max_depth: int = 20,
    max_segments: int = 4096,
    error_samples: int = 9,
) -> PiecewiseBezier:
    """Fit a smooth parametric curve with measured Euclidean sample error."""
    allowed = float(tolerance)
    if not math.isfinite(allowed) or allowed <= 0.0:
        raise ValueError("tolerance must be finite and positive")
    if max_depth < 0:
        raise ValueError("max_depth must be non-negative")
    if max_segments < 1:
        raise ValueError("max_segments must be positive")
    if error_samples < 3:
        raise ValueError("error_samples must be at least 3")
    if float(t0) == float(t1):
        raise ValueError("parameter interval must have non-zero width")

    accepted: list[CubicBezierSegment] = []

    def refine(start: float, end: float, depth: int) -> None:
        candidate = parametric_hermite(
            function(start),
            function(end),
            derivative(start),
            derivative(end),
            t0=start,
            t1=end,
        )
        error = _measured_error(function, candidate, start, end, error_samples)
        if error <= allowed:
            accepted.append(CubicBezierSegment(*candidate.control_points, fit_error=error))
            return
        if depth >= max_depth or len(accepted) + 2 > max_segments:
            raise ToleranceNotMet(
                f"measured error {error:g} exceeds tolerance {allowed:g} at depth {depth}"
            )
        midpoint = (start + end) / 2.0
        refine(start, midpoint, depth + 1)
        refine(midpoint, end, depth + 1)

    refine(float(t0), float(t1), 0)
    if len(accepted) > max_segments:
        raise ToleranceNotMet(f"fit requires more than {max_segments} segments")
    return PiecewiseBezier(accepted)


def fit_graph(
    function: Callable[[float], float],
    derivative: Callable[[float], float],
    *,
    x0: float,
    x1: float,
    tolerance: float,
    max_depth: int = 20,
    max_segments: int = 4096,
    error_samples: int = 9,
) -> PiecewiseBezier:
    """Fit ``y=f(x)`` under Euclidean ``(x, y)`` error tolerance."""
    return fit_parametric(
        lambda x: Point(x, function(x)),
        lambda x: Vector(1.0, derivative(x)),
        t0=x0,
        t1=x1,
        tolerance=tolerance,
        max_depth=max_depth,
        max_segments=max_segments,
        error_samples=error_samples,
    )
