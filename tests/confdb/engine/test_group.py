# ----------------------------------------------------------------------
# Test engine"s Group predicate
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.confdb.engine.base import Engine

CONF1 = [
    ["interfaces", "Fa0/1", "admin-status", "on"],
    ["interfaces", "Fa0/1", "type", "physical"],
    ["interfaces", "Fa0/1", "description", "client 1"],
    ["interfaces", "Fa0/2", "admin-status", "off"],
    ["interfaces", "Fa0/2", "type", "physical"],
    ["interfaces", "Fa0/2", "description", "client 2"],
    ["interfaces", "Fa0/3"],
]

CONF2 = [
    ["interfaces", "Fa0/1", "address", "1.2.3.4"],
    ["interfaces", "Fa0/1", "address", "5.6.7.8"],
    ["interfaces", "Fa0/2", "address", "1.1.1.1"],
    ["interfaces", "Fa0/3", "description", "test"],
]


@pytest.mark.parametrize(
    ("conf", "query", "output"),
    [
        (
            CONF1,
            """(
            Match("interfaces", name) or
            Match("interfaces", name, "type", type) or
            Match("interfaces", name, "description", description) or
            Match("interfaces", name, "admin-status", admin_status)
        ) and Group("name")""",
            [
                {
                    "admin_status": "on",
                    "description": "client 1",
                    "name": "Fa0/1",
                    "type": "physical",
                },
                {
                    "admin_status": "off",
                    "description": "client 2",
                    "name": "Fa0/2",
                    "type": "physical",
                },
                {"name": "Fa0/3"},
            ],
        ),
        (
            CONF2,
            """(
            Match("interfaces", name) or
            Match("interfaces", name, "address", address) or
            Match("interfaces", name, "description", description)
        ) and Group("name", stack={"address"})""",
            [
                {"address": ["1.2.3.4", "5.6.7.8"], "name": "Fa0/1"},
                {"address": ["1.1.1.1"], "name": "Fa0/2"},
                {"description": "test", "name": "Fa0/3"},
            ],
        ),
    ],
)
def test_group(conf, query, output):
    e = Engine()
    e.insert_bulk(conf)
    assert list(e.query(query)) == output
