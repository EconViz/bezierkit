from functools import lru_cache
from math import comb


class BinomialTable:
    """Cached binomial coefficients."""

    @staticmethod
    @lru_cache(maxsize=None)
    def coefficient(n: int, k: int) -> int:
        if n < 0 or k < 0 or k > n:
            raise ValueError(f"invalid binomial indices n={n}, k={k}")
        return comb(n, k)
