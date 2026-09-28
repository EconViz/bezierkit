"""Small capability interfaces for parametric curves."""

from bezierkit.core.capabilities.curve import ParametricCurve
from bezierkit.core.capabilities.differentiable import Differentiable
from bezierkit.core.capabilities.reversible import Reversible
from bezierkit.core.capabilities.subdividable import Subdividable

__all__ = ["Differentiable", "ParametricCurve", "Reversible", "Subdividable"]
