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


TS = 1621755589311551271
TS_DATE = "2021-05-23"
TS_STR = "2021-05-23 07:39:49"
LABELS = ["test"]


@pytest.mark.parametrize(
    "values,expected",
    [
        ({}, None),
        ({"m1": 1, "m2": 2}, {"date": TS_DATE, "ts": TS_STR, "labels": LABELS, "m1": 1, "m2": 2}),
        ({"m1": 1, "m2": None}, {"date": TS_DATE, "ts": TS_STR, "labels": LABELS, "m1": 1}),
    ],
)
def test_metrics(values, expected):
    cdag = NodeCDAG("metrics", {"scope": "test", "spool": False})
    # Check default inputs
    node = cdag.get_node()
    inputs = set(node.iter_inputs())
    assert inputs == {"ts", "labels"}
    assert node.allow_dynamic is True
    # Add dynamic inputs
    for k in values:
        node.add_input(k)
    inputs = set(node.iter_inputs())
    x_inputs = {"ts", "labels"}
    x_inputs.update({x for x in values})
    assert inputs == x_inputs
    # Activate dynamic inputs
    for k, v in values.items():
        if v is not None:
            cdag.activate(k, v)
    # Activate static inputs
    cdag.activate("ts", TS)
    cdag.activate("labels", LABELS)
    value = cdag.get_value()
    assert value == expected
