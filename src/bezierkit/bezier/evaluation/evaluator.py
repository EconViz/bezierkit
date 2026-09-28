from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np

from bezierkit.bezier.polygon import ControlPolygon


class Evaluator(ABC):
    """Strategy interface for evaluating a control polygon."""

    @abstractmethod
    def evaluate(self, polygon: ControlPolygon, t: np.ndarray) -> np.ndarray: ...
