# ----------------------------------------------------------------------
# Math functions test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from math import pi

# Third-party modules
import pytest

# NOC modules
from .util import NodeCDAG


@pytest.mark.parametrize(
    ("fn", "x", "expected"),
    [
        # neg
        ("neg", 0, 0),
        ("neg", 0.0, 0.0),
        ("neg", 1, -1),
        ("neg", 1.0, -1.0),
        ("neg", -1, 1),
        ("neg", -1.0, 1.0),
        # abs
        ("abs", -1, 1),
        ("abs", -1.0, 1.0),
        ("abs", 0, 0),
        ("abs", 0.0, 0.0),
        ("abs", 1, 1),
        ("abs", 1.0, 1.0),
        # sqrt
        ("sqrt", -1, None),
        ("sqrt", 0, 0.0),
        ("sqrt", 1.0, 1.0),
        ("sqrt", 4.0, 2.0),
        # exp
        ("exp", -1, 0.36787944117144233),
        ("exp", 0.0, 1.0),
        ("exp", 1.0, 2.718281828459045),
        # sin
        ("sin", 0.0, 0.0),
        ("sin", pi / 6, 0.5),
        ("sin", pi / 3, 0.8660254037844386),
        ("sin", pi / 2, 1.0),
        # cos
        ("cos", 0.0, 1.0),
        ("cos", pi / 6, 0.8660254037844386),
        ("cos", pi / 3, 0.5),
        ("cos", pi / 2, 0.0),
        # tan
        ("tan", 0.0, 0.0),
        ("tan", pi / 6, 0.5773502691896257),
        ("tan", pi / 3, 1.7320508075688767),
        ("tan", pi / 2, 1.633123935319537e16),
        # asin
        ("asin", 0.0, 0.0),
        ("asin", 0.5, pi / 6),
        ("asin", 0.8660254037844386, pi / 3),
        ("asin", 1.0, pi / 2),
        # acos
        ("acos", 1.0, 0.0),
        ("acos", 0.8660254037844386, pi / 6),
        ("acos", 0.5, pi / 3),
        ("acos", 0.0, pi / 2),
        # tan
        ("atan", 0.0, 0.0),
        ("atan", 0.5773502691896257, pi / 6),
        ("atan", 1.7320508075688767, pi / 3),
        ("atan", 1.633123935319537e16, pi / 2),
    ],
)
def test_math_node(fn, x, expected):
    cdag = NodeCDAG(fn)
    assert cdag.is_activated() is False
    cdag.activate("x", x)
    x_act = expected is not None
    assert cdag.is_activated() is x_act
    value = cdag.get_value()
    if expected is None:
        assert value is None
    else:
        assert value == pytest.approx(expected, rel=1e-4)
