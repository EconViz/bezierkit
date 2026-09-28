from __future__ import annotations

from abc import ABC, abstractmethod


class Reversible(ABC):
    """A value whose parameterization can be reversed."""

    @abstractmethod
    def reversed(self) -> Reversible: ...
