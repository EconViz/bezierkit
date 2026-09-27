from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

import numpy as np

from bezierkit.core.geometry.point import Point
from bezierkit.core.geometry.point_set import PointSet


@dataclass(frozen=True, slots=True, init=False)
class Sample:
    """Immutable parameter values paired with sampled points."""

    t: np.ndarray
    points: PointSet

    def __init__(self, t: np.ndarray, points: PointSet) -> None:
        values = np.array(t, dtype=float, copy=True)
        if values.ndim != 1:
            raise ValueError("sample parameters must be one-dimensional")
        if len(values) != points.count:
            raise ValueError(
                f"parameter count {len(values)} does not match point count {points.count}"
            )
        values.setflags(write=False)
        object.__setattr__(self, "t", values)
        object.__setattr__(self, "points", points)

    @property
    def x(self) -> np.ndarray:
        return self.points.x

    @property
    def y(self) -> np.ndarray:
        return self.points.y

    def __iter__(self) -> Iterator[tuple[float, Point]]:
        return ((float(t), point) for t, point in zip(self.t, self.points, strict=True))

    def __len__(self) -> int:
        return len(self.t)
