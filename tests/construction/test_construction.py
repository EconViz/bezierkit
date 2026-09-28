import pytest

from bezierkit.construction.construction import Construction


def test_construction_is_abstract() -> None:
    with pytest.raises(TypeError):
        Construction()
