import numpy as np

from bezierkit.bezier.evaluation.casteljau import DeCasteljauEvaluator
from bezierkit.bezier.evaluation.evaluator import Evaluator
from bezierkit.bezier.polygon import ControlPolygon


def test_evaluator_interface_is_abstract() -> None:
    try:
        Evaluator()
    except TypeError:
        pass
    else:
        raise AssertionError("Evaluator must be abstract")


def test_casteljau_evaluates_line_and_endpoints() -> None:
    polygon = ControlPolygon([[0, 0], [4, 2]])
    result = DeCasteljauEvaluator().evaluate(polygon, np.array([0, 0.5, 1]))
    assert np.allclose(result, [[0, 0], [2, 1], [4, 2]])


def test_casteljau_handles_constant_curve() -> None:
    polygon = ControlPolygon([[3, 7, 9]])
    result = DeCasteljauEvaluator().evaluate(polygon, np.array([0, 0.4, 1]))
    assert np.allclose(result, [[3, 7, 9]] * 3)


def test_casteljau_vectorized_matches_known_quadratic() -> None:
    polygon = ControlPolygon([[0, 0], [1, 2], [2, 0]])
    result = DeCasteljauEvaluator().evaluate(polygon, np.array([0.25, 0.75]))
    assert np.allclose(result, [[0.5, 0.75], [1.5, 0.75]])
