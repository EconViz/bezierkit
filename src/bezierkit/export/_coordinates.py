from __future__ import annotations

import math
from collections.abc import Callable

from bezierkit.core.geometry.point import Point

CoordinateTransform = Callable[[Point], Point]


def transformed(point: Point, transform: CoordinateTransform | None) -> Point:
    result = transform(point) if transform is not None else point
    if not isinstance(result, Point):
        raise TypeError("coordinate transform must return a Point")
    if result.dimension != 2:
        raise ValueError("text path exporters require two-dimensional points")
    return result


def number(value: float, precision: int) -> str:
    if not isinstance(precision, int) or precision < 0:
        raise ValueError("precision must be a non-negative integer")
    finite = float(value)
    if not math.isfinite(finite):
        raise ValueError("coordinates must be finite")
    if abs(finite) < 0.5 * 10 ** (-precision):
        finite = 0.0
    return f"{finite:.{precision}f}"
