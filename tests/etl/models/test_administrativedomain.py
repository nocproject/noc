# ----------------------------------------------------------------------
# AdministrativeDomainModel tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.etl.models.administrativedomain import AdministrativeDomain
from noc.core.etl.models.typing import Reference


@pytest.mark.parametrize(
    "input,expected",
    [
        # Incomplete items
        ((1,), ValueError),
        #
        (("1", "test"), {"id": "1", "name": "test", "parent": None, "default_pool": None}),
        (
            ("2", "test children", "1"),
            {"id": "2", "name": "test children", "parent": "1", "default_pool": None},
        ),
        (
            ("2", "test children", "1", "DEFAULT"),
            {"id": "2", "name": "test children", "parent": "1", "default_pool": "DEFAULT"},
        ),
        # Ignore excessive items
        (
            ("2", "test children", "1", "DEFAULT", "_"),
            {"id": "2", "name": "test children", "parent": "1", "default_pool": "DEFAULT"},
        ),
    ],
)
def test_from_iter(input, expected):
    if expected is ValueError:
        with pytest.raises(ValueError):
            AdministrativeDomain.from_iter(input)
    else:
        item = AdministrativeDomain.from_iter(input)
        for k, v in expected.items():
            field = getattr(item, k)
            if isinstance(field, Reference):
                assert field.value == v
            else:
                assert field == v
