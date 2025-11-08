# ----------------------------------------------------------------------
# Test engine's Set() predicate
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
        # Noop
        ({}, "Set()", [{}]),
        # Set one value to empty context
        ({}, "Set(x=1)", [{"x": 1}]),
        # Set two values to empty context
        ({}, "Set(x=1, y=2)", [{"x": 1, "y": 2}]),
        # Set one value to filled context
        ({"x": 1}, "Set(y=2)", [{"x": 1, "y": 2}]),
        # Overwrite value of context
        ({"x": 1, "y": 2}, "Set(x=3)", [{"x": 3, "y": 2}]),
        # Iterate single list over empty context
        ({}, "Set(x=[1, 2, 3])", [{"x": 1}, {"x": 2}, {"x": 3}]),
        # Product two lists over empty context
        (
            {},
            "Set(x=[1, 2], y=[3, 4])",
            [{"x": 1, "y": 3}, {"x": 2, "y": 3}, {"x": 1, "y": 4}, {"x": 2, "y": 4}],
        ),
        # Product two lists over filled context
        (
            {"z": 3},
            "Set(x=[1, 2], y=[3, 4])",
            [
                {"x": 1, "y": 3, "z": 3},
                {"x": 2, "y": 3, "z": 3},
                {"x": 1, "y": 4, "z": 3},
                {"x": 2, "y": 4, "z": 3},
            ],
        ),
        # Product two list over production context
        (
            {"z": [3, 7]},
            "Set(x=[1, 2], y=[3, 4])",
            [
                {"x": 1, "y": 3, "z": 3},
                {"x": 2, "y": 3, "z": 3},
                {"x": 1, "y": 4, "z": 3},
                {"x": 2, "y": 4, "z": 3},
                {"x": 1, "y": 3, "z": 7},
                {"x": 2, "y": 3, "z": 7},
                {"x": 1, "y": 4, "z": 7},
                {"x": 2, "y": 4, "z": 7},
            ],
        ),
        # Set after set
        ({"z": 3}, "Set(x=1) and Set(y=2)", [{"x": 1, "y": 2, "z": 3}]),
        ({"z": 3}, "Set(x=1, y=2) and Set(k=3)", [{"k": 3, "x": 1, "y": 2, "z": 3}]),
        # Arithmetic expressions
        ({"x": 1}, "Set(y=x + 1)", [{"x": 1, "y": 2}]),
        ({"x": 1}, "Set(x=x + 1)", [{"x": 2}]),
        ({"x": [1, 2, 3]}, "Set(y=x + 1)", [{"x": 1, "y": 2}, {"x": 2, "y": 3}, {"x": 3, "y": 4}]),
        (
            {"x": [1, 2], "y": [3, 4]},
            "Set(z=x * y + 5)",
            [
                {"x": 1, "y": 3, "z": 8},
                {"x": 2, "y": 3, "z": 11},
                {"x": 1, "y": 4, "z": 9},
                {"x": 2, "y": 4, "z": 13},
            ],
        ),
        # Arbitrary python expression
        ({"x": [1, 2]}, "Set(y='x=%s' % x)", [{"x": 1, "y": "x=1"}, {"x": 2, "y": "x=2"}]),
        # List in expression
        (
            {"x": [1, 2]},
            "Set(y=[3, 4])",
            [{"x": 1, "y": 3}, {"x": 1, "y": 4}, {"x": 2, "y": 3}, {"x": 2, "y": 4}],
        ),
        # Deduplication
        ({"x": [1, 2, 3, 4]}, "Set(x=x%2)", [{"x": 1}, {"x": 0}]),
        # Or
        (
            {"x": [1, 2, 3]},
            "Set(y=1) or Set(y=2)",
            [
                {"x": 1, "y": 1},
                {"x": 2, "y": 1},
                {"x": 3, "y": 1},
                {"x": 1, "y": 2},
                {"x": 2, "y": 2},
                {"x": 3, "y": 2},
            ],
        ),
    ],
)
def test_set(input, query, output):
    assert check_query(query, input, output)
