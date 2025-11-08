# ----------------------------------------------------------------------
# Test engine's NotMatch function
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.confdb.engine.base import Engine
from noc.core.confdb.db.base import ConfDB

CONF1 = [
    ["interfaces", "Fa 0/1", "description", "First interface"],
    ["interfaces", "Fa 0/2", "description", "Second interface"],
    ["interfaces", "Fa 0/3", "description", "Third interface"],
]

EMPTY_CONF = []


@pytest.mark.parametrize(
    ("conf", "query", "output"),
    [
        # Match incomplete
        (CONF1, "NotMatch('interfaces', x, 'description')", []),
        (
            CONF1,
            "NotMatch('interfaces', x, 'admin-status')",
            [{"x": "Fa 0/1"}, {"x": "Fa 0/2"}, {"x": "Fa 0/3"}],
        ),
        # # Complete match (empty context)
        (CONF1, "NotMatch('interfaces', 'Fa 0/1', 'description', 'First interface')", []),
        (CONF1, "NotMatch('interfaces', 'Fa 0/1', 'description', 'First interface!')", [{}]),
        # Match last unbound variable
        (CONF1, "NotMatch('interfaces', 'Fa 0/1', 'description', x)", []),
        # Match two unbound variables
        (CONF1, "NotMatch('interfaces', x, 'description', y)", []),
        # Match placeholder
        (CONF1, "NotMatch('interfaces', _x, 'admin-status')", [{}, {}, {}]),
        # Empty config, bound
        (EMPTY_CONF, "NotMatch('interfaces', 'Fa0/1', 'admin-status')", [{}]),
        # Empty config, unbound
        (EMPTY_CONF, "NotMatch('interfaces', x, 'admin-status')", []),
        # Partial path, bound
        (
            CONF1,
            "Set(x=['a', 'b', 'c']) and NotMatch('protocols', 'cdp', 'interface', x)",
            [{"x": "a"}, {"x": "b"}, {"x": "c"}],
        ),
    ],
)
def test_match(conf, query, output):
    db = ConfDB()
    db.insert_bulk(conf)
    e = Engine().with_db(db)
    assert list(e.query(query)) == output
