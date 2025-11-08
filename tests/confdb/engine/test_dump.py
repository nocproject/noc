# ----------------------------------------------------------------------
# Test engine's Dump predicate
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
        ({}, "Dump()", [{}]),
        # Filled context
        ({"x": 1}, "Dump()", [{"x": 1}]),
        # Production
        ({"x": [1, 2]}, "Dump()", [{"x": 1}, {"x": 2}]),
        # With message
        # Empty context
        ({}, "Dump('M1')", [{}]),
        # Filled context
        ({"x": 1}, "Dump('M2')", [{"x": 1}]),
        # Production
        ({"x": [1, 2]}, "Dump('M3')", [{"x": 1}, {"x": 2}]),
    ],
)
def test_dump(input, query, output):
    e = Engine()
    assert list(e.query(query, **input)) == output
