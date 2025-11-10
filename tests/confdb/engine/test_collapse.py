# ----------------------------------------------------------------------
# Test engine's Collapse predicate
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.confdb.engine.base import Engine

CONF1 = [
    ["interfaces", "Fa0/1", "tagged-vlans", "1,2,3-4"],
    ["interfaces", "Fa0/1", "tagged-vlans", "5-10,25"],
    ["interfaces", "Fa0/2", "description", "test"],
    ["interfaces", "Fa0/3", "tagged-vlans", "5-10,19"],
    ["interfaces", "Fa0/3", "tagged-vlans", "20-30,35"],
    ["interfaces", "Fa0/4", "tagged-vlans", "11"],
]

RESULT_JOIN = """interfaces
    Fa0/1
        tagged-vlans
            1,2,3-4,5-10,25
    Fa0/2
        description
            test
    Fa0/3
        tagged-vlans
            5-10,19,20-30,35
    Fa0/4
        tagged-vlans
            11"""


RESULT_JOINRANGE = """interfaces
    Fa0/1
        tagged-vlans
            1-10,25
    Fa0/2
        description
            test
    Fa0/3
        tagged-vlans
            5-10,19-30,35
    Fa0/4
        tagged-vlans
            11"""


@pytest.mark.parametrize(
    ("conf", "query", "result"),
    [
        (CONF1, "Collapse('interfaces', X, 'tagged-vlans', join=',')", RESULT_JOIN),
        (CONF1, "Collapse('interfaces', X, 'tagged-vlans', joinrange=',')", RESULT_JOINRANGE),
    ],
)
def test_collapse_join(conf, query, result):
    e = Engine()
    e.insert_bulk(CONF1)
    list(e.query(query))
    assert e.dump("indent") == result
