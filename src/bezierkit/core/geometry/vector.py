from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from bezierkit.core.errors import DimensionMismatch


@dataclass(frozen=True, slots=True, init=False)
class Vector:
    """An immutable vector in n-dimensional Euclidean space."""

    coords: tuple[float, ...]

    def __init__(self, *coords: float) -> None:
        if not coords:
            raise ValueError("Vector requires at least one coordinate")
        values = tuple(float(value) for value in coords)
        if not all(math.isfinite(value) for value in values):
            raise ValueError("Vector coordinates must be finite")
        object.__setattr__(self, "coords", values)

    @property
    def dimension(self) -> int:
        return len(self.coords)

    def as_array(self) -> np.ndarray:
        return np.asarray(self.coords, dtype=float).copy()

    def _require_same_dimension(self, other: Vector) -> None:
        if self.dimension != other.dimension:
            raise DimensionMismatch(
                f"vector dimensions differ: {self.dimension} and {other.dimension}"
            )

    def __add__(self, other: Vector) -> Vector:
        self._require_same_dimension(other)
        return Vector(*(a + b for a, b in zip(self.coords, other.coords, strict=True)))

    def __sub__(self, other: Vector) -> Vector:
        self._require_same_dimension(other)
        return Vector(*(a - b for a, b in zip(self.coords, other.coords, strict=True)))

    def __mul__(self, scalar: float) -> Vector:
        return Vector(*(value * float(scalar) for value in self.coords))

    def __rmul__(self, scalar: float) -> Vector:
        return self * scalar

    def dot(self, other: Vector) -> float:
        self._require_same_dimension(other)
        return sum(a * b for a, b in zip(self.coords, other.coords, strict=True))

    def norm(self) -> float:
        return math.sqrt(self.dot(self))

    def normalized(self) -> Vector:
        norm = self.norm()
        if norm == 0.0:
            raise ValueError("cannot normalize a zero vector")
        return self * (1.0 / norm)
