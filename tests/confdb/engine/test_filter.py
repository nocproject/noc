# ----------------------------------------------------------------------
# Test engine's Filter predicate
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from .utils import check_query


@pytest.mark.parametrize(
    ("input", "query", "output"),
    [
        # Pass
        ({}, "Filter(True)", [{}]),
        ({"x": [1, 2]}, "Filter(True)", [{"x": 1}, {"x": 2}]),
        # Cut
        ({}, "Filter(False)", []),
        ({"x": [1, 2]}, "Filter(False)", []),
        # Even
        ({"x": [1, 2, 3, 4]}, "Filter(x % 2 == 0)", [{"x": 2}, {"x": 4}]),
        # Complex expression
        (
            {"x": [1, 2, 3, 4], "y": [1, 2, 3, 4]},
            "Filter(x > y)",
            [
                {"x": 2, "y": 1},
                {"x": 3, "y": 1},
                {"x": 4, "y": 1},
                {"x": 3, "y": 2},
                {"x": 4, "y": 2},
                {"x": 4, "y": 3},
            ],
        ),
    ],
)
def test_filter(input, query, output):
    assert check_query(query, input, output)
