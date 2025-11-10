# ----------------------------------------------------------------------
# Test engine's MatchExactVLAN predicate
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
        ({}, "MatchExactVLAN('5', '100-200')", []),
        ({}, "MatchExactVLAN('1-1000', '1-1000')", [{}]),
        ({}, "MatchExactVLAN('5,10-20', '100-200')", []),
        ({}, "MatchExactVLAN('11-15', '11-15')", [{}]),
        # Bound variables
        (
            {"vlan": ["5", "10", "15", "20", "25"]},
            "MatchExactVLAN('10-20', vlan)",
            [],
        ),
        (
            {"vf": ["5", "5,10-20"], "vlan": ["3", "5", "10-20", "25"]},
            "MatchExactVLAN(vf, vlan)",
            [
                {"vf": "5", "vlan": "5"},
            ],
        ),
        (
            {"vf": ["5", "5,10-20"], "vlan": [3, 5, "10-20", 25]},
            "MatchExactVLAN(vf, vlan)",
            [
                {"vf": "5", "vlan": 5},
            ],
        ),
    ],
)
def test_match_exact_vlan(input, query, output):
    e = Engine()
    assert list(e.query(query, **input)) == output
