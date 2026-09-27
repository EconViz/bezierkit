"""A small mathematical toolkit for constructing and analyzing Bézier curves."""

from bezierkit.bezier.curve import BezierCurve
from bezierkit.core.errors import (
    BezierKitError,
    DegreeError,
    DimensionMismatch,
    ParameterOutOfDomain,
)
from bezierkit.core.geometry.point import Point
from bezierkit.core.geometry.vector import Vector

__version__ = "0.2.0"

__all__ = [
    "BezierCurve",
    "BezierKitError",
    "DegreeError",
    "DimensionMismatch",
    "ParameterOutOfDomain",
    "Point",
    "Vector",
    "__version__",
]
