from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, init=False)
class Vector:
    """An immutable vector in n-dimensional Euclidean space."""

    coords: tuple[float, ...]

    def __init__(self, *coords: float) -> None:
        if not coords:
            raise ValueError("Vector requires at least one coordinate")
        object.__setattr__(self, "coords", tuple(float(value) for value in coords))

    @property
    def dimension(self) -> int:
        return len(self.coords)
