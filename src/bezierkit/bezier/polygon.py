from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike

from bezierkit.core.errors import DegreeError
from bezierkit.core.geometry.point import Point
from bezierkit.core.geometry.point_set import PointSet


@dataclass(frozen=True, slots=True, init=False)
class ControlPolygon:
    """An immutable sequence of control points."""

    points: PointSet

    def __init__(self, points: PointSet | ArrayLike | Iterable[Point]) -> None:
        if isinstance(points, PointSet):
            values: object = points.array
        else:
            values = points
        try:
            count = len(values)  # type: ignore[arg-type]
        except TypeError as exc:
            raise ValueError("control points must be a sized collection") from exc
        if count == 0:
            raise DegreeError("a control polygon requires at least one point")
        object.__setattr__(self, "points", PointSet(values))

    @property
    def degree(self) -> int:
        return self.points.count - 1

    @property
    def dimension(self) -> int:
        return self.points.dimension

    def differences(self) -> np.ndarray:
        return np.diff(self.points.array, axis=0)
