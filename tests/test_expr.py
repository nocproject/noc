# ----------------------------------------------------------------------
# noc.core.expr tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.expr import get_vars, get_fn


@pytest.mark.parametrize(
    ("expr", "expected"),
    [
        ("1", []),
        ("x", ["x"]),
        ("x + 1", ["x"]),
        ("x + y", ["x", "y"]),
        ("1 + y + x", ["x", "y"]),
        ("sin(y + x) / 3", ["x", "y"]),
        ("(delta * 8) / time_delta", ["delta", "time_delta"]),
    ],
)
def test_get_vars(expr, expected):
    vars = get_vars(expr)
    assert vars == expected


@pytest.mark.parametrize(
    ("expr", "args", "expected"),
    [
        ("1", {}, 1),
        ("x", {"x": 1}, 1),
        ("x + 1", {"x": 2}, 3),
        ("(x + y) // 2", {"x": 1, "y": 3}, 2),
        ("(delta * 8) / time_delta", {"delta": 100, "time_delta": 10}, 80),
    ],
)
def test_get_fn(expr, args, expected):
    fn = get_fn(expr)
    value = fn(**args)
    assert value == expected
