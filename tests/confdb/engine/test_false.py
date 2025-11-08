# ----------------------------------------------------------------------
# Test engine's False predicate
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
        ({}, "False()", []),
        # Filled context
        ({"x": 1}, "False()", []),
        # Production
        ({"x": [1, 2]}, "False()", []),
        # Twice Empty context
        ({}, "False() and False()", []),
        # Twice Filled context
        ({"x": 1}, "False() and False()", []),
        # Twice Production
        ({"x": [1, 2]}, "False() and False()", []),
        # False after Set
        ({}, "Set(x=1) and False()", []),
        ({}, "Set(x=[1, 2]) and False()", []),
    ],
)
def test_false(input, query, output):
    e = Engine()
    assert list(e.query(query, **input)) == output
