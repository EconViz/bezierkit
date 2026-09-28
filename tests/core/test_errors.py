import pytest

from bezierkit.core.errors import (
    BezierKitError,
    DegreeError,
    DimensionMismatch,
    ParameterOutOfDomain,
    ToleranceNotMet,
)


@pytest.mark.parametrize(
    "error", [DegreeError, DimensionMismatch, ParameterOutOfDomain, ToleranceNotMet]
)
def test_public_errors_share_package_base(error: type[Exception]) -> None:
    assert issubclass(error, BezierKitError)


def test_error_preserves_message() -> None:
    with pytest.raises(DimensionMismatch, match="expected 2, got 3"):
        raise DimensionMismatch("expected 2, got 3")
