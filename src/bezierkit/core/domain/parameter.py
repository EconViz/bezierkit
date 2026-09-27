from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from bezierkit.core.domain.interval import Interval
from bezierkit.core.errors import ParameterOutOfDomain


@dataclass(frozen=True, slots=True, init=False)
class ParameterValues:
    """Validated, immutable parameter values."""

    array: np.ndarray

    def __init__(self, values: np.ndarray) -> None:
        array = np.array(values, dtype=float, copy=True)
        if array.ndim != 1 or array.size == 0:
            raise ValueError("ParameterValues requires a non-empty one-dimensional array")
        array.setflags(write=False)
        object.__setattr__(self, "array", array)

    @classmethod
    def from_input(
        cls, value: float | Iterable[float] | np.ndarray, *, domain: Interval
    ) -> ParameterValues:
        array = np.atleast_1d(np.asarray(value, dtype=float))
        if array.ndim != 1:
            raise ValueError("parameter input must be scalar or one-dimensional")
        invalid = (~np.isfinite(array)) | (array < domain.start) | (array > domain.end)
        if np.any(invalid):
            raise ParameterOutOfDomain(
                f"parameter value(s) {array[invalid].tolist()} outside domain "
                f"[{domain.start}, {domain.end}]"
            )
        return cls(array)

    def __len__(self) -> int:
        return len(self.array)
