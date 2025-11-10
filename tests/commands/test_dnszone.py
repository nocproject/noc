# ----------------------------------------------------------------------
# dnszone command test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# Python modules
from noc.commands.dnszone import Command


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        # Empty value
        ("", 0),
        ("1", 1),
        ("100", 100),
        ("10s", 10),
        ("10S", 10),
        ("10m", 600),
        ("10M", 600),
        ("10h", 36000),
        ("10H", 36000),
        ("10d", 864000),
        ("10D", 864000),
        ("10w", 6048000),
        ("10W", 6048000),
        ("5d2", 432002),
        ("5d2S", 432002),
        ("5D2h1", 439201),
    ],
)
def test_ttl(value, expected):
    assert Command.parse_ttl(value) == expected
