# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Test engine's Group predicate
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
    ["interfaces", "Fa0/3"]
]


@pytest.mark.parametrize("conf,query,output", [
    (CONF1, """(
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
             "type": "physical"
         },
         {
             "admin_status": "off",
             "description": "client 2",
             "name": "Fa0/2",
             "type": "physical"
         },
         {
             "name": "Fa0/3"
         }
     ]
    )
])
def test_group(conf, query, output):
    e = Engine()
    e.insert_bulk(conf)
    assert list(e.query(query)) == output
