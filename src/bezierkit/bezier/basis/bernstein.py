from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from bezierkit.bezier.basis.binomial import BinomialTable


@dataclass(frozen=True, slots=True)
class BernsteinBasis:
    """Bernstein basis polynomials of a fixed degree."""

    degree: int

    def __post_init__(self) -> None:
        if self.degree < 0:
            raise ValueError("Bernstein degree must be non-negative")

    def __call__(self, t: float) -> np.ndarray:
        indices = np.arange(self.degree + 1)
        coefficients = np.array(
            [BinomialTable.coefficient(self.degree, int(index)) for index in indices],
            dtype=float,
        )
        return coefficients * float(t) ** indices * (1.0 - float(t)) ** (self.degree - indices)

    def matrix(self, t: np.ndarray) -> np.ndarray:
        values = np.asarray(t, dtype=float)
        if values.ndim != 1:
            raise ValueError("BernsteinBasis.matrix requires a one-dimensional array")
        indices = np.arange(self.degree + 1)
        coefficients = np.array(
            [BinomialTable.coefficient(self.degree, int(index)) for index in indices],
            dtype=float,
        )
        columns = indices[np.newaxis, :]
        parameters = values[:, np.newaxis]
        return (
            coefficients[np.newaxis, :]
            * parameters**columns
            * (1.0 - parameters) ** (self.degree - columns)
        )
