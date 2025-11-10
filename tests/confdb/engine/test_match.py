# ----------------------------------------------------------------------
# Test engine's Match function
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.confdb.engine.base import Engine

CONF1 = [
    ["system", "hostname", "h1"],
    ["interface", "Fa 0/1", "description", "First interface"],
    ["interface", "Fa 0/2", "description", "Second interface"],
    ["interface", "Fa 0/3", "description", "Third interface"],
]


@pytest.mark.parametrize(
    ("conf", "query", "output"),
    [
        # Exact match
        (CONF1, "Match('interface')", [{}]),
        # Exact mismatch
        (CONF1, "Match('absent')", []),
        # Match incomplete
        (
            CONF1,
            "Match('interface', x, 'description')",
            [{"x": "Fa 0/1"}, {"x": "Fa 0/2"}, {"x": "Fa 0/3"}],
        ),
        # Complete match (empty context)
        (CONF1, "Match('interface', 'Fa 0/1', 'description', 'First interface')", [{}]),
        # No match
        (CONF1, "Match('interface', 'Fa 0/1', 'description', 'First interface!')", []),
        # Match one unbound variable
        (CONF1, "Match('interface', 'Fa 0/1', 'description', x)", [{"x": "First interface"}]),
        # Match two unbound variables
        (
            CONF1,
            "Match('interface', x, 'description', y)",
            [
                {"x": "Fa 0/1", "y": "First interface"},
                {"x": "Fa 0/2", "y": "Second interface"},
                {"x": "Fa 0/3", "y": "Third interface"},
            ],
        ),
        # Match one bound variable
        (
            CONF1,
            "Set(x='Fa 0/1') and Match('interface', x, 'description', 'First interface')",
            [{"x": "Fa 0/1"}],
        ),
        (
            CONF1,
            "Set(x='First interface') and Match('interface', 'Fa 0/1', 'description', x)",
            [{"x": "First interface"}],
        ),
        # Match one bound one unbound
        (
            CONF1,
            "Set(x='Fa 0/1') and Match('interface', x, 'description', y)",
            [{"x": "Fa 0/1", "y": "First interface"}],
        ),
        # Match production
        (
            CONF1,
            "Set(x=['Fa 0/1', 'Fa 0/2']) and Match('interface', x, 'description', y)",
            [{"x": "Fa 0/1", "y": "First interface"}, {"x": "Fa 0/2", "y": "Second interface"}],
        ),
        # Match placeholder
        (
            CONF1,
            "Set(x=['Fa 0/1', 'Fa 0/2']) and Match('interface', x, 'description', _y)",
            [{"x": "Fa 0/1"}, {"x": "Fa 0/2"}],
        ),
    ],
)
def test_match(conf, query, output):
    e = Engine()
    e.insert_bulk(conf)
    assert list(e.query(query)) == output
