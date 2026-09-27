from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class Interval:
    """An immutable closed interval."""

    start: float
    end: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.start) or not math.isfinite(self.end):
            raise ValueError("Interval bounds must be finite")
        if self.start > self.end:
            raise ValueError(f"Interval start ({self.start}) must be <= end ({self.end})")

    def contains(self, value: float, *, tolerance: float = 1e-12) -> bool:
        return math.isfinite(value) and self.start - tolerance <= value <= self.end + tolerance

    def clamp(self, value: float) -> float:
        return min(max(value, self.start), self.end)

    def linspace(self, count: int) -> np.ndarray:
        return np.linspace(self.start, self.end, count)
