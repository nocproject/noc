# ----------------------------------------------------------------------
# Comparison operations test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from .util import NodeCDAG


@pytest.mark.parametrize(
    ("op", "conf", "x", "y", "expected"),
    [
        # ==
        ("eq", {}, 0, 0, 1),
        ("eq", {}, 0, 1, 0),
        ("eq", {"true_level": 3}, 1, 1, 3),
        ("eq", {"false_level": -3}, 1, 0, -3),
        ("eq", {"epsilon": 0.01}, 1.0, 1.0, 1),
        ("eq", {"epsilon": 0.01}, 1.0, 1.001, 1),
        ("eq", {"epsilon": 0.01}, 1.0, 1.1, 0),
        ("ne", {}, 0, 0, 0),
        ("ne", {}, 0, 1, 1),
        ("ne", {"false_level": -3}, 1, 1, -3),
        ("ne", {"true_level": 3}, 1, 0, 3),
        ("ne", {"epsilon": 0.01}, 1.0, 1.0, 0),
        ("ne", {"epsilon": 0.01}, 1.0, 1.001, 0),
        ("ne", {"epsilon": 0.01}, 1.0, 1.1, 1),
    ],
)
def test_comp_node(op, conf, x, y, expected):
    cdag = NodeCDAG(op, config=conf)
    assert cdag.is_activated() is False
    cdag.activate("x", x)
    assert cdag.is_activated() is False
    cdag.activate("y", y)
    assert cdag.is_activated() is True
    value = cdag.get_value()
    if expected is None:
        assert value is None
    else:
        assert value == pytest.approx(expected)
