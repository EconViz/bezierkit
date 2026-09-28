from abc import ABC, abstractmethod
from typing import Generic, TypeVar

C = TypeVar("C")


class Construction(ABC, Generic[C]):
    """A specification object that builds a value of type ``C``."""

    @abstractmethod
    def build(self) -> C: ...
