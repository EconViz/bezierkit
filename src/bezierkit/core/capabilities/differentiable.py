from __future__ import annotations

from abc import ABC, abstractmethod


class Differentiable(ABC):
    """A value that can produce a representation of its derivative."""

    @abstractmethod
    def derivative(self, order: int = 1) -> Differentiable: ...
