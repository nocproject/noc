# ----------------------------------------------------------------------
# Test engine's HasVLAN predicate
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
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
        ({}, "HasVLAN('5', 1)", []),
        ({}, "HasVLAN('5', 5)", [{}]),
        ({}, "HasVLAN('5,10-20', 4)", []),
        ({}, "HasVLAN('5,10-20', 5)", [{}]),
        # Bound variables
        (
            {"vlan": ["5", "10", "15", "20", "25"]},
            "HasVLAN('10-20', vlan)",
            [{"vlan": "10"}, {"vlan": "15"}, {"vlan": "20"}],
        ),
        (
            {"vf": ["5", "5,10-20"], "vlan": ["3", "5", "10", "15", "20", "25"]},
            "HasVLAN(vf, vlan)",
            [
                {"vf": "5", "vlan": "5"},
                {"vf": "5,10-20", "vlan": "5"},
                {"vf": "5,10-20", "vlan": "10"},
                {"vf": "5,10-20", "vlan": "15"},
                {"vf": "5,10-20", "vlan": "20"},
            ],
        ),
    ],
)
def test_has_vlan(input, query, output):
    e = Engine()
    assert list(e.query(query, **input)) == output
