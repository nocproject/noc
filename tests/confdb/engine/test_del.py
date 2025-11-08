# ----------------------------------------------------------------------
# Test engine's Del predicate
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
        ({}, "Del('x')", [{}]),
        ({}, "Del(x)", [{}]),
        # Unbound
        ({"x": 1, "y": 2}, "Del('x')", [{"y": 2}]),
        # Bound
        ({"x": 1, "y": 2}, "Del(x)", [{"y": 2}]),
        # Multi
        ({"x": 1, "y": 2, "z": 3}, "Del(x, 'y')", [{"z": 3}]),
        # Deduplication
        ({"x": [1, 2], "y": [3, 4]}, "Del(x)", [{"y": 3}, {"y": 4}]),
    ],
)
def test_true(input, query, output):
    e = Engine()
    assert list(e.query(query, **input)) == output
