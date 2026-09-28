"""Benchmark typical sampled-contour simplification workloads."""

from __future__ import annotations

import json
import math
import platform
import statistics
import time

import numpy as np

from bezierkit import Point
from bezierkit.fitting import fit_polyline

SIZES = (400, 4_000, 40_000)
REPEATS = 5


def main() -> None:
    results = []
    for size in SIZES:
        values = np.linspace(0.0, 8.0 * math.pi, size)
        points = [Point(value, math.sin(value)) for value in values]
        durations = []
        output_segments = 0
        for _ in range(REPEATS):
            start = time.perf_counter()
            path = fit_polyline(points, tolerance=0.01, preserve_corners=False)
            durations.append(time.perf_counter() - start)
            output_segments = len(path.segments)
        results.append(
            {
                "input_points": size,
                "output_segments": output_segments,
                "median_seconds": statistics.median(durations),
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
