import numpy as np
import pytest
from matplotlib.path import Path
from matplotlib.transforms import Affine2D, Transform

from bezierkit import Point
from bezierkit.adapters.matplotlib import (
    approximate_path,
    from_path,
    to_path,
)


class SquareXTransform(Transform):
    input_dims = 2
    output_dims = 2
    is_separable = False
    has_inverse = False

    def transform_non_affine(self, values: np.ndarray) -> np.ndarray:
        result = np.asarray(values, dtype=float).copy()
        result[:, 0] **= 2
        return result


def mixed_path() -> Path:
    vertices = np.asarray(
        [
            (0, 0),
            (1, 0),
            (1.5, 1),
            (2, 0),
            (2.5, -1),
            (3.5, 1),
            (4, 0),
            (10, 0),
            (11, 0),
            (11, 1),
            (10, 0),
        ],
        dtype=float,
    )
    codes = np.asarray(
        [
            Path.MOVETO,
            Path.LINETO,
            Path.CURVE3,
            Path.CURVE3,
            Path.CURVE4,
            Path.CURVE4,
            Path.CURVE4,
            Path.MOVETO,
            Path.LINETO,
            Path.LINETO,
            Path.CLOSEPOLY,
        ],
        dtype=np.uint8,
    )
    return Path(vertices, codes)


def test_matplotlib_path_preserves_commands_subpaths_and_closure() -> None:
    converted = from_path(mixed_path())
    assert len(converted.subpaths) == 2
    assert tuple(subpath.closed for subpath in converted.subpaths) == (False, True)
    assert len(converted.subpaths[0].segments) == 3
    assert all(segment.as_curve().degree == 3 for segment in converted)

    round_trip = to_path(converted)
    assert Path.CURVE4 in round_trip.codes
    assert Path.CURVE3 not in round_trip.codes
    assert round_trip.codes[-1] == Path.CLOSEPOLY


def test_affine_transform_is_applied_exactly_to_every_control() -> None:
    transform = Affine2D().scale(2, -3).translate(5, 7)
    converted = from_path(mixed_path(), transform=transform)
    first = converted.segments[0]
    assert first.p0 == Point(5, 7)
    assert first.p3 == Point(7, 7)


def test_non_affine_transform_requires_explicit_approximation() -> None:
    transform = SquareXTransform()
    with pytest.raises(ValueError, match="non-affine"):
        from_path(mixed_path(), transform=transform)
    approximated = approximate_path(mixed_path(), transform, tolerance=0.01)
    assert approximated.dimension == 2
    assert approximated.segments[0].p0 == Point(0, 0)
