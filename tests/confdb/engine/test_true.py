# ----------------------------------------------------------------------
# Test engine's True predicate
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
        # Empty context
        ({}, "True()", [{}]),
        # Filled context
        ({"x": 1}, "True()", [{"x": 1}]),
        # Production
        ({"x": [1, 2]}, "True()", [{"x": 1}, {"x": 2}]),
        # Twice Empty context
        ({}, "True() and True()", [{}]),
        # Twice Filled context
        ({"x": 1}, "True() and True()", [{"x": 1}]),
        # Twice Production
        ({"x": [1, 2]}, "True() and True()", [{"x": 1}, {"x": 2}]),
        # True after Set
        ({}, "Set(x=1) and True()", [{"x": 1}]),
        ({}, "Set(x=[1, 2]) and True()", [{"x": 1}, {"x": 2}]),
    ],
)
def test_true(input, query, output):
    e = Engine()
    assert list(e.query(query, **input)) == output
