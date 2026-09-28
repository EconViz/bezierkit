from __future__ import annotations

import numpy as np

from bezierkit.bezier.basis.bernstein import BernsteinBasis
from bezierkit.bezier.evaluation.evaluator import Evaluator
from bezierkit.bezier.polygon import ControlPolygon


class BernsteinEvaluator(Evaluator):
    """Vectorized batch evaluation using a Bernstein basis matrix.

    This evaluator is optimized for renderer-sized batches. Use
    :class:`DeCasteljauEvaluator` when maximum numerical stability for high
    degree curves is more important than batch throughput.
    """

    def evaluate(self, polygon: ControlPolygon, t: np.ndarray) -> np.ndarray:
        values = np.asarray(t, dtype=float)
        if values.ndim != 1:
            raise ValueError("evaluator parameter values must be one-dimensional")
        basis = BernsteinBasis(polygon.degree).matrix(values)
        return basis @ polygon.points.array
