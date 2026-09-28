from __future__ import annotations

import numpy as np

from bezierkit.bezier.polygon import ControlPolygon
from bezierkit.core.errors import ParameterOutOfDomain


class Subdivider:
    """de Casteljau subdivision and segment extraction."""

    @staticmethod
    def _validate(t: float) -> float:
        value = float(t)
        if not 0.0 <= value <= 1.0:
            raise ParameterOutOfDomain(f"parameter {value} outside domain [0.0, 1.0]")
        return value

    @classmethod
    def split(cls, polygon: ControlPolygon, t: float) -> tuple[ControlPolygon, ControlPolygon]:
        value = cls._validate(t)
        work = polygon.points.array.copy()
        left = [work[0].copy()]
        right = [work[-1].copy()]
        while len(work) > 1:
            work = (1.0 - value) * work[:-1] + value * work[1:]
            left.append(work[0].copy())
            right.append(work[-1].copy())
        return ControlPolygon(np.stack(left)), ControlPolygon(np.stack(right[::-1]))

    @classmethod
    def segment(cls, polygon: ControlPolygon, t0: float, t1: float) -> ControlPolygon:
        start = cls._validate(t0)
        end = cls._validate(t1)
        if start > end:
            raise ValueError(f"t0 ({start}) must be <= t1 ({end})")
        if start == end:
            left, _ = cls.split(polygon, start)
            return ControlPolygon([left.points[-1]])
        prefix, _ = cls.split(polygon, end)
        _, segment = cls.split(prefix, start / end)
        return segment
