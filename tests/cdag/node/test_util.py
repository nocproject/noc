# ----------------------------------------------------------------------
# Test util functions
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from .util import NodeCDAG


@pytest.mark.parametrize(
    "op,config,x,key,expected",
    [
        # key
        ("key", {}, 1.0, 0.0, None),
        ("key", {}, 2.0, 1.0, 2.0),
    ],
)
def test_key_node(op, config, x, key, expected):
    cdag = NodeCDAG(op, config=config)
    cdag.activate("key", key)
    cdag.activate("x", x)
    value = cdag.get_value()
    if expected is None:
        assert value is None
    else:
        assert value == pytest.approx(expected, rel=1e-4)


@pytest.mark.parametrize("config,expected", [({"value": 1}, 1), ({"value": 1.0}, 1.0)])
def test_value_node(config, expected):
    cdag = NodeCDAG("value", config=config)
    assert cdag.get_node().config.value == config["value"]
    assert cdag.get_node().is_const is True
    assert cdag.get_value() == expected


@pytest.mark.parametrize(
    "op,x,expected",
    [
        ("one", 0, 0),
        ("one", 1, 1),
        ("one", 1.0, 1.0),
        ("none", 0, None),
        ("none", 1, None),
        ("none", 1.0, None),
    ],
)
def test_util_node(op, x, expected):
    cdag = NodeCDAG(op)
    cdag.activate("x", x)
    assert cdag.get_value() == expected
