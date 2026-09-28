from __future__ import annotations

from dataclasses import dataclass

from bezierkit.core.capabilities.curve import ParametricCurve
from bezierkit.sampling.sample import Sample
from bezierkit.sampling.sampler import Sampler


@dataclass(frozen=True, slots=True)
class UniformSampler(Sampler):
    """Sample a curve at uniformly spaced parameter values."""

    count: int

    def __post_init__(self) -> None:
        if self.count < 2:
            raise ValueError("sample count must be at least 2")

    def sample(self, curve: ParametricCurve) -> Sample:
        t = curve.domain.linspace(self.count)
        return Sample(t, curve.at_many(t))
