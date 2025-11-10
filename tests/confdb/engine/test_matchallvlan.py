# ----------------------------------------------------------------------
# Test engine's MatchAllVLAN predicate
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
        ({}, "MatchAllVLAN('5', '100-200')", []),
        ({}, "MatchAllVLAN('1-2000', '1-1000')", [{}]),
        ({}, "MatchAllVLAN('5,10-20', '100-200')", []),
        ({}, "MatchAllVLAN('5,10-20', '11-15')", [{}]),
        # Bound variables
        (
            {"vlan": ["5", "10", "15", "20", "25"]},
            "MatchAllVLAN('10-20', vlan)",
            [{"vlan": "10"}, {"vlan": "15"}, {"vlan": "20"}],
        ),
        (
            {"vf": ["5", "5,10-20"], "vlan": ["3", "5", "10", "15", "20", "25"]},
            "MatchAllVLAN(vf, vlan)",
            [
                {"vf": "5", "vlan": "5"},
                {"vf": "5,10-20", "vlan": "5"},
                {"vf": "5,10-20", "vlan": "10"},
                {"vf": "5,10-20", "vlan": "15"},
                {"vf": "5,10-20", "vlan": "20"},
            ],
        ),
        (
            {"vf": ["5", "5,10-20"], "vlan": [3, 5, 10, 15, 20, 25]},
            "MatchAllVLAN(vf, vlan)",
            [
                {"vf": "5", "vlan": 5},
                {"vf": "5,10-20", "vlan": 5},
                {"vf": "5,10-20", "vlan": 10},
                {"vf": "5,10-20", "vlan": 15},
                {"vf": "5,10-20", "vlan": 20},
            ],
        ),
    ],
)
def test_match_all_vlan(input, query, output):
    e = Engine()
    assert list(e.query(query, **input)) == output
