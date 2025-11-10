# ----------------------------------------------------------------------
# Test Sprintf function
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
        # Empty context
        ({}, "Set(x=1) and Sprintf(y, 'x = %s', x)", [{"x": 1, "y": "x = 1"}]),
        # Empty context and constant
        ({}, "Set(x=1) and Sprintf(y, 'x = %s, y = %s', x, '2')", [{"x": 1, "y": "x = 1, y = 2"}]),
        # Filled context
        ({"x": 1}, "Sprintf(y, 'x = %s', x)", [{"x": 1, "y": "x = 1"}]),
        # Production
        (
            {"x": [1, 2]},
            "Sprintf(y, 'x = %s', x)",
            [{"x": 1, "y": "x = 1"}, {"x": 2, "y": "x = 2"}],
        ),
        # Multi-argument production
        (
            {"x": [1, 2], "y": [3, 4]},
            "Sprintf(z, 'x = %s, y = %s', x, y)",
            [
                {"x": 1, "y": 3, "z": "x = 1, y = 3"},
                {"x": 2, "y": 3, "z": "x = 2, y = 3"},
                {"x": 1, "y": 4, "z": "x = 1, y = 4"},
                {"x": 2, "y": 4, "z": "x = 2, y = 4"},
            ],
        ),
        # Check context processing order
        ({}, "Set(x=1) and Sprintf(y, 'x = %s', x) and Set(x=2)", [{"x": 2, "y": "x = 1"}]),
        # Multi-sprintf
        (
            {},
            "Set(x=1) and Sprintf(y, 'x = %s', x) and Set(x=2) and Sprintf(y, 'x = %s', x)",
            [{"x": 2, "y": "x = 2"}],
        ),
        (
            {},
            "Set(x=1) and Sprintf(y, 'x = %s', x) and Set(x=2) and Sprintf(z, 'x = %s', x)",
            [{"x": 2, "y": "x = 1", "z": "x = 2"}],
        ),
        # Output to placeholder
        ({"x": [1, 2]}, "Sprintf(_y, 'x = %s', x)", [{"x": 1}, {"x": 2}]),
        # Expression
        ({"x": 1}, "Sprintf(y, 'y = %s', x + 1)", [{"x": 1, "y": "y = 2"}]),
    ],
)
def test_sprintf(input, query, output):
    assert check_query(query, input, output)
