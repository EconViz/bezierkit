import numpy as np
import pytest

from bezierkit.bezier.evaluation.casteljau import DeCasteljauEvaluator
from bezierkit.bezier.operations.subdivision import Subdivider
from bezierkit.bezier.polygon import ControlPolygon
from bezierkit.core.errors import ParameterOutOfDomain


def evaluate(polygon: ControlPolygon, t: float) -> np.ndarray:
    return DeCasteljauEvaluator().evaluate(polygon, np.array([t]))[0]


def test_split_preserves_join_and_original_parameterization() -> None:
    polygon = ControlPolygon([[0, 0], [1, 2], [3, 2], [4, 0]])
    left, right = Subdivider.split(polygon, 0.3)
    expected = evaluate(polygon, 0.3)
    assert np.allclose(evaluate(left, 1), expected)
    assert np.allclose(evaluate(right, 0), expected)


def test_segment_reparameterizes_requested_interval() -> None:
    polygon = ControlPolygon([[0, 0], [1, 2], [3, 2], [4, 0]])
    segment = Subdivider.segment(polygon, 0.25, 0.75)
    assert np.allclose(evaluate(segment, 0), evaluate(polygon, 0.25))
    assert np.allclose(evaluate(segment, 1), evaluate(polygon, 0.75))


def test_zero_length_segment_is_constant_at_parameter() -> None:
    polygon = ControlPolygon([[0, 0], [2, 2]])
    segment = Subdivider.segment(polygon, 0.4, 0.4)
    assert segment.degree == 0
    assert np.allclose(segment.points.array, [[0.8, 0.8]])


@pytest.mark.parametrize("t", [-0.1, 1.1])
def test_split_rejects_out_of_domain_parameter(t: float) -> None:
    with pytest.raises(ParameterOutOfDomain):
        Subdivider.split(ControlPolygon([[0, 0], [1, 1]]), t)


def test_segment_rejects_reversed_interval() -> None:
    with pytest.raises(ValueError, match="t0"):
        Subdivider.segment(ControlPolygon([[0, 0], [1, 1]]), 0.8, 0.2)
