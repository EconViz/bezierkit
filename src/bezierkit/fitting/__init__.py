"""Tolerance-controlled curve and polyline fitting."""

from bezierkit.fitting.adaptive import fit_graph, fit_parametric, hermite_error_bound
from bezierkit.fitting.polyline import fit_polyline, maximum_polyline_deviation

__all__ = [
    "fit_graph",
    "fit_parametric",
    "fit_polyline",
    "hermite_error_bound",
    "maximum_polyline_deviation",
]
