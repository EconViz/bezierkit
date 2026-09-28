import pytest

from bezierkit.bezier.basis.binomial import BinomialTable


def test_binomial_coefficients() -> None:
    assert [BinomialTable.coefficient(4, i) for i in range(5)] == [1, 4, 6, 4, 1]


@pytest.mark.parametrize("n,k", [(-1, 0), (2, -1), (2, 3)])
def test_binomial_rejects_invalid_indices(n: int, k: int) -> None:
    with pytest.raises(ValueError):
        BinomialTable.coefficient(n, k)
