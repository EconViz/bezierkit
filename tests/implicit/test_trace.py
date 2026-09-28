import math

from bezierkit.implicit import trace_implicit


def test_trace_circle_preserves_closed_component() -> None:
    contours = trace_implicit(
        lambda x, y: x * x + y * y,
        levels=[1.0],
        viewport=(-1.5, 1.5, -1.5, 1.5),
        resolution=(81, 81),
        tolerance=0.01,
    )
    paths = contours.for_level(1.0)
    assert len(paths) == 1
    assert paths[0].closed
    radii = [math.hypot(segment.p0.x, segment.p0.y) for segment in paths[0]]
    assert max(abs(radius - 1.0) for radius in radii) < 0.02


def test_trace_preserves_multiple_disconnected_components() -> None:
    contours = trace_implicit(
        lambda x, y: (x * x + y * y - 1) * ((x - 3) ** 2 + y * y - 1),
        levels=0.0,
        viewport=(-1.5, 4.5, -1.5, 1.5),
        resolution=(121, 81),
        tolerance=0.02,
    )
    assert len(contours.for_level(0.0)) == 2
    assert all(path.closed for path in contours.for_level(0.0))


def test_trace_x_squared_y_level_set_and_multiple_levels() -> None:
    contours = trace_implicit(
        lambda x, y: x * x * y,
        levels=[1.0, 2.0],
        viewport=(0.5, 3.0, 0.0, 5.0),
        resolution=(81, 81),
        tolerance=0.02,
    )
    assert contours.level_values == (1.0, 2.0)
    assert all(contours.for_level(level) for level in contours.level_values)


def test_optional_gradient_produces_non_collinear_tangent_controls() -> None:
    without = trace_implicit(
        lambda x, y: x * x + y * y,
        levels=1,
        viewport=(-1.5, 1.5, -1.5, 1.5),
        resolution=(25, 25),
        tolerance=0.05,
    ).for_level(1)[0]
    with_gradient = trace_implicit(
        lambda x, y: x * x + y * y,
        levels=1,
        viewport=(-1.5, 1.5, -1.5, 1.5),
        resolution=(25, 25),
        tolerance=0.05,
        gradient=lambda x, y: (2 * x, 2 * y),
    ).for_level(1)[0]
    assert any(
        abs((segment.p1 - segment.p0).coords[0] * (segment.p3 - segment.p0).coords[1]
            - (segment.p1 - segment.p0).coords[1] * (segment.p3 - segment.p0).coords[0])
        > 1e-8
        for segment in with_gradient
    )
    assert len(without.segments) > 0
