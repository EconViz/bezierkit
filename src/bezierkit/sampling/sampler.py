from __future__ import annotations

from abc import ABC, abstractmethod

from bezierkit.core.capabilities.curve import ParametricCurve
from bezierkit.sampling.sample import Sample


class Sampler(ABC):
    """Strategy interface for sampling any parametric curve."""

    @abstractmethod
    def sample(self, curve: ParametricCurve) -> Sample: ...
