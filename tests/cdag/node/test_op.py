# ----------------------------------------------------------------------
# Test OpNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from .util import NodeCDAG


@pytest.mark.parametrize(
    ("op", "x", "y", "expected"),
    [
        # +
        ("add", 0, 0, 0),
        ("add", 1, 2, 3),
        ("add", 1.0, 2.0, 3.0),
        ("add", 1.0, 2, 3.0),
        # -
        ("sub", 0, 0, 0),
        ("sub", 2, 1, 1),
        ("sub", 1.0, 2.0, -1.0),
        ("sub", 1.0, 2, -1.0),
        # *
        ("mul", 0, 1, 0),
        ("mul", 1, 2, 2),
        ("mul", 1.0, 2.0, 2.0),
        ("mul", 1.0, 2, 2.0),
        # /
        ("div", 0, 0, None),
        ("div", 1, 0, None),
        ("div", 2, 1, 2),
        ("div", 1.0, 2.0, 0.5),
        ("div", 1.0, 2, 0.5),
    ],
)
def test_op_node(op, x, y, expected):
    cdag = NodeCDAG(op)
    assert cdag.is_activated() is False
    cdag.activate("x", x)
    assert cdag.is_activated() is False
    cdag.activate("y", y)
    x_act = expected is not None
    assert cdag.is_activated() is x_act
    value = cdag.get_value()
    if expected is None:
        assert value is None
    else:
        assert value == expected
