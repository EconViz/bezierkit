import numpy as np
import pytest

from bezierkit.core.domain.interval import Interval
from bezierkit.core.domain.parameter import ParameterValues
from bezierkit.core.errors import ParameterOutOfDomain


def test_parameter_values_normalize_scalar_and_iterable() -> None:
    domain = Interval(0, 1)
    assert np.allclose(ParameterValues.from_input(0.5, domain=domain).array, [0.5])
    assert np.allclose(ParameterValues.from_input([0, 0.5, 1], domain=domain).array, [0, 0.5, 1])


@pytest.mark.parametrize("value", [-0.1, 1.1, float("nan"), float("inf")])
def test_parameter_values_reject_invalid_values(value: float) -> None:
    with pytest.raises(ParameterOutOfDomain):
        ParameterValues.from_input(value, domain=Interval(0, 1))


def test_parameter_values_are_read_only() -> None:
    values = ParameterValues.from_input([0, 1], domain=Interval(0, 1))
    with pytest.raises(ValueError):
        values.array[0] = 0.5


def test_public_parameter_array_cannot_mutate_storage() -> None:
    values = ParameterValues.from_input([0, 1], domain=Interval(0, 1))
    exposed = values.array
    exposed.setflags(write=True)
    exposed[:] = [0.2, 0.8]
    exposed.resize((1, 2), refcheck=False)
    assert np.allclose(values.array, [0, 1])
