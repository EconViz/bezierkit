"""A small mathematical toolkit for constructing and analyzing Bézier curves."""

from bezierkit.bezier.curve import BezierCurve
from bezierkit.bezier.path import BezierSubpath, PiecewiseBezier
from bezierkit.bezier.segment import CubicBezierSegment
from bezierkit.core.errors import (
    BezierKitError,
    DegreeError,
    DimensionMismatch,
    ParameterOutOfDomain,
)
from bezierkit.core.geometry.point import Point
from bezierkit.core.geometry.vector import Vector

__version__ = "0.3.0"

__all__ = [
    "BezierCurve",
    "BezierKitError",
    "BezierSubpath",
    "CubicBezierSegment",
    "DegreeError",
    "DimensionMismatch",
    "ParameterOutOfDomain",
    "PiecewiseBezier",
    "Point",
    "Vector",
    "__version__",
]
