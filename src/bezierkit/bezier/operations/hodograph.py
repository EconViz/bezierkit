from __future__ import annotations

import numpy as np

from bezierkit.bezier.polygon import ControlPolygon


class Hodograph:
    """Construct derivative control polygons."""

    @staticmethod
    def of(polygon: ControlPolygon) -> ControlPolygon:
        if polygon.degree == 0:
            return ControlPolygon(np.zeros((1, polygon.dimension)))
        return ControlPolygon(polygon.degree * polygon.differences())
