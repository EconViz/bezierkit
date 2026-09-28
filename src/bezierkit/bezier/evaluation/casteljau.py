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
        control = polygon.points.array
        work = np.broadcast_to(control, (len(values), *control.shape)).copy()
        parameters = values[:, np.newaxis, np.newaxis]
        for remaining in range(polygon.degree, 0, -1):
            work[:, :remaining] = (
                (1.0 - parameters) * work[:, :remaining]
                + parameters * work[:, 1 : remaining + 1]
            )
        return work[:, 0]
