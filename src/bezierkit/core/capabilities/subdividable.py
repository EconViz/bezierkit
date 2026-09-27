from __future__ import annotations

from abc import ABC, abstractmethod


class Subdividable(ABC):
    """A value that can be split or restricted to a segment."""

    @abstractmethod
    def split(self, t: float) -> tuple[Subdividable, Subdividable]: ...

    @abstractmethod
    def segment(self, t0: float, t1: float) -> Subdividable: ...
