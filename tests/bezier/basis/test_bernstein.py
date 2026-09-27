import numpy as np
import pytest

from bezierkit.bezier.basis.bernstein import BernsteinBasis


@pytest.mark.parametrize("degree", [0, 1, 3, 8])
def test_bernstein_partition_of_unity(degree: int) -> None:
    basis = BernsteinBasis(degree)
    for t in [0, 0.2, 0.5, 1]:
        assert basis(t).sum() == pytest.approx(1)


def test_bernstein_endpoint_values() -> None:
    basis = BernsteinBasis(3)
    assert np.allclose(basis(0), [1, 0, 0, 0])
    assert np.allclose(basis(1), [0, 0, 0, 1])


def test_bernstein_matrix_matches_scalar_calls() -> None:
    basis = BernsteinBasis(4)
    values = np.array([0, 0.25, 0.7, 1])
    assert np.allclose(basis.matrix(values), np.stack([basis(t) for t in values]))


def test_bernstein_rejects_negative_degree() -> None:
    with pytest.raises(ValueError):
        BernsteinBasis(-1)
