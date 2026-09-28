from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

import numpy as np

from bezierkit.core.domain.interval import Interval
from bezierkit.core.geometry.point import Point
from bezierkit.core.geometry.point_set import PointSet


class ParametricCurve(ABC):
    """A curve from a parameter interval into Euclidean space."""

    @property
    @abstractmethod
    def dimension(self) -> int: ...

    @property
    @abstractmethod
    def domain(self) -> Interval: ...

    @abstractmethod
    def at(self, t: float) -> Point: ...

    @abstractmethod
    def at_many(self, t: Iterable[float] | np.ndarray) -> PointSet: ...

    def __call__(self, t: float) -> Point:
        return self.at(t)
