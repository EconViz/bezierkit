class BezierKitError(Exception):
    """Base class for errors intended for bezierkit users."""


class DimensionMismatch(BezierKitError):
    """Raised when geometric values have incompatible dimensions."""


class DegreeError(BezierKitError):
    """Raised when a curve degree is invalid for an operation."""


class ParameterOutOfDomain(BezierKitError):
    """Raised when a parameter lies outside a curve's domain."""
