from __future__ import annotations

import numpy as np

from bezierkit.bezier.evaluation.evaluator import Evaluator
from bezierkit.bezier.polygon import ControlPolygon


class DeCasteljauEvaluator(Evaluator):
    """Numerically stable evaluation using de Casteljau's algorithm."""

    def evaluate(self, polygon: ControlPolygon, t: np.ndarray) -> np.ndarray:
        values = np.asarray(t, dtype=float)
        if values.ndim != 1:
            raise ValueError("evaluator parameter values must be one-dimensional")
        result = np.empty((len(values), polygon.dimension), dtype=float)
        control = polygon.points.array
        for row, value in enumerate(values):
            work = control.copy()
            for remaining in range(polygon.degree, 0, -1):
                work[:remaining] = (
                    (1.0 - value) * work[:remaining] + value * work[1 : remaining + 1]
                )
            result[row] = work[0]
        return result
