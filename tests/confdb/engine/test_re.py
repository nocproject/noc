# ----------------------------------------------------------------------
# Test engine's Re function
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
        # Empty context, unknown variable
        ({}, r"Re(r'\d+', x)", []),
        # Empty context, constant string
        ({}, r"Re(r'\d+', 'x')", []),
        # Match context
        ({"x": "12"}, r"Re(r'\d+', x)", [{"x": "12"}]),
        # Match context, pass groups
        ({"x": "12"}, r"Re(r'-?(?P<abs>\d+)', x)", [{"x": "12", "abs": "12"}]),
        (
            {"x": ["12", "-12"]},
            r"Re(r'-?(?P<abs>\d+)', x)",
            [{"x": "12", "abs": "12"}, {"x": "-12", "abs": "12"}],
        ),
        # Ignore case
        ({"x": ["a", "b", "A", "B"]}, "Re('a+', x)", [{"x": "a"}]),
        ({"x": ["a", "b", "A", "B"]}, "Re('a+', x, ignore_case=True)", [{"x": "a"}, {"x": "A"}]),
        # Variable pattern
        (
            {"x": ["ge-0/0/0", "xe-1/0/0", "ge-0/0/1"], "pattern": "ge-.+"},
            "Re(pattern, x)",
            [{"pattern": "ge-.+", "x": "ge-0/0/0"}, {"pattern": "ge-.+", "x": "ge-0/0/1"}],
        ),
    ],
)
def test_re(input, query, output):
    e = Engine()
    assert list(e.query(query, **input)) == output
