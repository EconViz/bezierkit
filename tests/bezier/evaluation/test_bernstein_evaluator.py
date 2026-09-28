import numpy as np

from bezierkit.bezier.evaluation.bernstein import BernsteinEvaluator
from bezierkit.bezier.evaluation.casteljau import DeCasteljauEvaluator
from bezierkit.bezier.polygon import ControlPolygon


def test_vectorized_bernstein_matches_de_casteljau() -> None:
    polygon = ControlPolygon([[0, 0, 1], [1, 3, -2], [4, 2, 5], [7, -1, 2]])
    parameters = np.linspace(0.0, 1.0, 10_000)

    actual = BernsteinEvaluator().evaluate(polygon, parameters)
    expected = DeCasteljauEvaluator().evaluate(polygon, parameters)

    assert np.allclose(actual, expected, rtol=1e-12, atol=1e-12)


def test_vectorized_bernstein_handles_constant_curve() -> None:
    polygon = ControlPolygon([[2, -3]])
    result = BernsteinEvaluator().evaluate(polygon, np.array([0.0, 0.2, 1.0]))
    assert np.array_equal(result, [[2, -3], [2, -3], [2, -3]])
