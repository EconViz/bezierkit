from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

from bezierkit.core.errors import DimensionMismatch

if TYPE_CHECKING:
    from bezierkit.core.geometry.vector import Vector


@dataclass(frozen=True, slots=True, init=False)
class Point:
    """An immutable point in n-dimensional Euclidean space."""

    coords: tuple[float, ...]

    def __init__(self, *coords: float) -> None:
        if not coords:
            raise ValueError("Point requires at least one coordinate")
        object.__setattr__(self, "coords", tuple(float(value) for value in coords))

    @property
    def dimension(self) -> int:
        return len(self.coords)

    def _coordinate(self, index: int, name: str) -> float:
        if self.dimension <= index:
            raise AttributeError(f"Point has no {name}-coordinate (dimension < {index + 1})")
        return self.coords[index]

    @property
    def x(self) -> float:
        return self._coordinate(0, "x")

    @property
    def y(self) -> float:
        return self._coordinate(1, "y")

    @property
    def z(self) -> float:
        return self._coordinate(2, "z")

    def as_array(self) -> np.ndarray:
        return np.asarray(self.coords, dtype=float).copy()

    def __add__(self, other: Vector) -> Point:
        if self.dimension != other.dimension:
            raise DimensionMismatch(
                f"point dimension {self.dimension} does not match vector dimension {other.dimension}"
            )
        return Point(*(a + b for a, b in zip(self.coords, other.coords, strict=True)))

    def __sub__(self, other: Point) -> Vector:
        from bezierkit.core.geometry.vector import Vector

        if self.dimension != other.dimension:
            raise DimensionMismatch(
                f"point dimensions differ: {self.dimension} and {other.dimension}"
            )
        return Vector(*(a - b for a, b in zip(self.coords, other.coords, strict=True)))
