# ----------------------------------------------------------------------
# Test engine's Fact predicate
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.confdb.db.base import ConfDB
from noc.core.confdb.engine.base import Engine

CONF1 = [
    ["interfaces", "Fa 0/1", "admin-status", "true"],
    ["interfaces", "Fa 0/2", "admin-status", "true"],
    ["interfaces", "Fa 0/3", "admin-status", "false"],
]

OUT1 = """interfaces
    Fa 0/1
        admin-status
            true
    Fa 0/2
        admin-status
            true
    Fa 0/3
        admin-status
            false
    Fa 0/4
        admin-status
            true"""

OUT2 = """interfaces
    Fa 0/1
        admin-status
            true
        description
            x
    Fa 0/2
        admin-status
            true
        description
            x
    Fa 0/3
        admin-status
            false"""

OUT3 = """interfaces
    Fa 0/1
        admin-status
            true
        description
            up
    Fa 0/2
        admin-status
            true
        description
            up
    Fa 0/3
        admin-status
            false"""


@pytest.mark.parametrize(
    ("conf", "input", "query", "out_conf", "output"),
    [
        # Fixed
        (CONF1, {}, "Fact('interfaces', 'Fa 0/4', 'admin-status', 'true')", OUT1, [{}]),
        # Bound var
        (
            CONF1,
            {"name": ["Fa 0/1", "Fa 0/2"]},
            "Fact('interfaces', name, 'description', 'x')",
            OUT2,
            [{"name": "Fa 0/1"}, {"name": "Fa 0/2"}],
        ),
        # Unbound var
        (
            CONF1,
            {},
            "Match('interfaces', name, 'admin-status', 'true') and Fact('interfaces', name, 'description', 'up')",
            OUT3,
            [{"name": "Fa 0/1"}, {"name": "Fa 0/2"}],
        ),
    ],
)
def test_fact(conf, input, query, out_conf, output):
    db = ConfDB()
    db.insert_bulk(CONF1)
    e = Engine().with_db(db)
    assert list(e.query(query, **input)) == output
    assert db.marshall("indent") == out_conf
