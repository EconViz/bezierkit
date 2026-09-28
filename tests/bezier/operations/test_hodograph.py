import numpy as np

from bezierkit.bezier.evaluation.casteljau import DeCasteljauEvaluator
from bezierkit.bezier.operations.hodograph import Hodograph
from bezierkit.bezier.polygon import ControlPolygon


def test_cubic_hodograph_obeys_endpoint_derivative_theorem() -> None:
    polygon = ControlPolygon([[0, 0], [1, 2], [3, 2], [4, 0]])
    derivative = Hodograph.of(polygon)
    values = DeCasteljauEvaluator().evaluate(derivative, np.array([0, 1]))
    assert np.allclose(values, [[3, 6], [3, -6]])


def test_line_hodograph_is_constant() -> None:
    derivative = Hodograph.of(ControlPolygon([[1, 2], [4, 8]]))
    assert derivative.degree == 0
    assert np.allclose(derivative.points.array, [[3, 6]])


def test_constant_hodograph_is_zero_constant() -> None:
    derivative = Hodograph.of(ControlPolygon([[3, 7, 9]]))
    assert derivative.degree == 0
    assert np.allclose(derivative.points.array, [[0, 0, 0]])
