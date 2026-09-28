import numpy as np
import pytest

from bezierkit.core.geometry.point import Point
from bezierkit.core.geometry.point_set import PointSet
from bezierkit.sampling.sample import Sample


def test_sample_delegates_coordinates_and_iterates_pairs() -> None:
    sample = Sample(np.array([0, 0.5, 1]), PointSet([[0, 1], [2, 3], [4, 5]]))
    assert np.allclose(sample.x, [0, 2, 4])
    assert np.allclose(sample.y, [1, 3, 5])
    assert list(sample) == [
        (0.0, Point(0, 1)),
        (0.5, Point(2, 3)),
        (1.0, Point(4, 5)),
    ]


def test_sample_requires_matching_counts() -> None:
    with pytest.raises(ValueError, match="count"):
        Sample(np.array([0, 1]), PointSet([[0, 0]]))


def test_sample_copies_and_freezes_parameters() -> None:
    source = np.array([0.0, 1.0])
    sample = Sample(source, PointSet([[0, 0], [1, 1]]))
    source[0] = 9
    assert sample.t[0] == 0
    with pytest.raises(ValueError):
        sample.t[0] = 0.5


def test_public_sample_parameters_cannot_mutate_storage() -> None:
    sample = Sample(np.array([0.0, 1.0]), PointSet([[0, 0], [1, 1]]))
    exposed = sample.t
    exposed.setflags(write=True)
    exposed[:] = [0.25, 0.75]
    exposed.resize((1, 2), refcheck=False)
    assert np.allclose(sample.t, [0, 1])
