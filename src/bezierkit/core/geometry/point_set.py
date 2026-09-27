from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator

import numpy as np
from numpy.typing import ArrayLike

from bezierkit.core.geometry.point import Point


@dataclass(frozen=True, slots=True, init=False)
class PointSet:
    """An immutable batch of points backed by an ``(count, dimension)`` array."""

    array: np.ndarray

    def __init__(self, values: ArrayLike | Iterable[Point]) -> None:
        materialized = list(values) if not isinstance(values, np.ndarray) else values
        if len(materialized) > 0 and isinstance(materialized[0], Point):
            materialized = [point.coords for point in materialized]
        array = np.array(materialized, dtype=float, copy=True)
        if array.ndim != 2:
            raise ValueError(f"PointSet requires a 2D array, got shape {array.shape}")
        if 0 in array.shape:
            raise ValueError("PointSet requires at least one point and one dimension")
        array.setflags(write=False)
        object.__setattr__(self, "array", array)

    @property
    def count(self) -> int:
        return int(self.array.shape[0])

    @property
    def dimension(self) -> int:
        return int(self.array.shape[1])

    def _column(self, index: int, name: str) -> np.ndarray:
        if self.dimension <= index:
            raise AttributeError(f"PointSet has no {name} column (dimension < {index + 1})")
        return self.array[:, index]

    @property
    def x(self) -> np.ndarray:
        return self._column(0, "x")

    @property
    def y(self) -> np.ndarray:
        return self._column(1, "y")

    @property
    def z(self) -> np.ndarray:
        return self._column(2, "z")

    def __iter__(self) -> Iterator[Point]:
        return (Point(*row) for row in self.array)

    def __len__(self) -> int:
        return self.count

    def __getitem__(self, index: int) -> Point:
        return Point(*self.array[index])
