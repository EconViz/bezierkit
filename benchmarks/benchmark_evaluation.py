"""Reproducible batch-evaluation benchmark for the two public strategies."""

from __future__ import annotations

import json
import platform
import statistics
import time

import numpy as np

from bezierkit.bezier.evaluation import BernsteinEvaluator, DeCasteljauEvaluator
from bezierkit.bezier.polygon import ControlPolygon

SIZES = (400, 10_000, 100_000)
REPEATS = 7


class ScalarDeCasteljauReference:
    """The v0.2 per-parameter loop retained only as a benchmark baseline."""

    def evaluate(self, polygon: ControlPolygon, t: np.ndarray) -> np.ndarray:
        result = np.empty((len(t), polygon.dimension), dtype=float)
        control = polygon.points.array
        for row, value in enumerate(t):
            work = control.copy()
            for remaining in range(polygon.degree, 0, -1):
                work[:remaining] = (
                    (1.0 - value) * work[:remaining] + value * work[1 : remaining + 1]
                )
            result[row] = work[0]
        return result


def elapsed_seconds(evaluator: object, polygon: ControlPolygon, values: np.ndarray) -> float:
    samples = []
    for _ in range(REPEATS):
        start = time.perf_counter()
        evaluator.evaluate(polygon, values)  # type: ignore[attr-defined]
        samples.append(time.perf_counter() - start)
    return statistics.median(samples)


def main() -> None:
    polygon = ControlPolygon([[0, 0], [1, 3], [4, 2], [7, -1]])
    casteljau = DeCasteljauEvaluator()
    bernstein = BernsteinEvaluator()
    scalar = ScalarDeCasteljauReference()
    results = []
    for size in SIZES:
        values = np.linspace(0.0, 1.0, size)
        stable = casteljau.evaluate(polygon, values)
        fast = bernstein.evaluate(polygon, values)
        scalar_seconds = elapsed_seconds(scalar, polygon, values)
        casteljau_seconds = elapsed_seconds(casteljau, polygon, values)
        bernstein_seconds = elapsed_seconds(bernstein, polygon, values)
        results.append(
            {
                "parameters": size,
                "scalar_reference_seconds": scalar_seconds,
                "de_casteljau_seconds": casteljau_seconds,
                "bernstein_seconds": bernstein_seconds,
                "de_casteljau_speedup": scalar_seconds / casteljau_seconds,
                "max_abs_difference": float(np.max(np.abs(stable - fast))),
            }
        )
    print(
        json.dumps(
            {
                "python": platform.python_version(),
                "platform": platform.platform(),
                "numpy": np.__version__,
                "repeats": REPEATS,
                "results": results,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
