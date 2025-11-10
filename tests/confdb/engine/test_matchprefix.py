# ----------------------------------------------------------------------
# Test engine's MatchPrefix predicate
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
# Third-party modules
import pytest

# NOC modules
from noc.core.confdb.engine.base import Engine


@pytest.mark.parametrize(
    ("input", "query", "output"),
    [
        # Constants
        ({}, "MatchPrefix('10.216.0.0/24', '192.168.0.1')", []),
        ({}, "MatchPrefix('192.168.100.0/24', '192.168.100.1')", [{}]),
        ({}, "MatchPrefix('10.0.0.0/16', '11.0.0.100')", []),
        ({}, "MatchPrefix('10.0.0.0/16', '10.0.0.100')", [{}]),
        # Bound variables
        (
            {"address": "192.168.100.1"},
            "MatchPrefix('192.168.100.0/16', address)",
            [{"address": "192.168.100.1"}],
        ),
        (
            {"prefix": "192.168.100.0/16", "address": "192.168.100.1"},
            "MatchPrefix(prefix, address)",
            [{"prefix": "192.168.100.0/16", "address": "192.168.100.1"}],
        ),
        (
            {"prefix": "192.168.100.0/16", "address": "192.169.100.1"},
            "MatchPrefix(prefix, address)",
            [],
        ),
    ],
)
def test_match_prefix(input, query, output):
    e = Engine()
    assert list(e.query(query, **input)) == output
