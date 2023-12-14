# ----------------------------------------------------------------------
# Lambda discriminator tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.discriminator import discriminator


@pytest.mark.parametrize(
    "v",
    [
        "trash",
        "unknown::xxx",
        "lambda::",
        "lambda::100a",
        "lambda::100-b",
        "lambda::1-2-3",
        "vlan::xxx",
        "vlan::-10",
        "vlan::4096",
        "vlan::100-10000",
    ],
)
def test_invalid_value(v: str) -> None:
    with pytest.raises(ValueError):
        discriminator(v)


@pytest.mark.parametrize(
    ("x", "y", "expected"),
    [
        ("lambda::100", "lambda::100", True),
        ("lambda::100", "lambda::100-10", True),
        ("lambda::100-10", "lambda::100", False),
        ("lambda::100-50", "lambda::50-10", False),
        ("lambda::100-50", "lambda::60-10", True),
        ("lambda::100-50", "lambda::140-10", True),
        ("lambda::100-50", "lambda::150-10", False),
        ("lambda::100-50", "lambda::100-60", False),
        ("lambda::100-50", "lambda::200-50", False),
        #
        ("vlan::1", "vlan::1", True),
        ("vlan::1", "vlan::2", False),
        ("vlan::1,2,7-15", "vlan::12", True),
        ("vlan::1,2,7-15", "vlan::12-15", True),
    ],
)
def test_contains(x: str, y: str, expected: str) -> None:
    d1 = discriminator(x)
    d2 = discriminator(y)
    assert (d2 in d1) is expected
