# ----------------------------------------------------------------------
# Test util functions
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from .util import NodeCDAG, publish_service


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


@pytest.mark.parametrize(
    "config,values,expected,state",
    [
        # Default levels
        (
            {},
            [0.0, 0.5, 0.99, 1.0, 1.5, 1.0, 0.99, 0.5, 0.0],
            [None, None, None, "raise", None, None, "clear", None, None],
            [False, False, False, True, True, True, False, False, False],
        ),
        # Hysteresis
        (
            {"activation_level": 1.0, "deactivation_level": 0.5},
            [0.0, 0.5, 0.99, 1.0, 1.5, 1.0, 0.99, 0.5, 0.49, 0.2, 0.0],
            [None, None, None, "raise", None, None, None, None, "clear", None, None],
            [False, False, False, True, True, True, True, True, False, False, False],
        ),
    ],
)
def test_alarm(config, values, expected, state):
    assert len(values) == len(expected), "Broken test"
    assert len(values) == len(state), "Broken test"
    default_cfg = {
        "reference": "test:1",
        "pool": "TEST",
        "partition": 3,
        "alarm_class": "Test",
        "managed_object": "777",
        "labels": ["l1", "l2"],
    }
    cfg = default_cfg.copy()
    cfg.update(config)
    cdag = NodeCDAG("alarm", cfg)
    node = cdag.get_node()
    with publish_service() as svc:
        for v, exp, st in zip(values, expected, state):
            cdag.begin()
            cdag.activate("x", v)
            # Check state change
            assert node.state.active is st, "Invalid state"
            # Check published messages
            messages = list(svc.iter_published())
            if not messages:
                # No message sent
                assert exp is None, "Lost message"
                continue
            assert len(messages) == 1, "Multiple message sent"
            assert exp is not None, "Unexpected message sent"
            msg = messages[0]
            # Check $op is set
            assert "$op" in msg.value
            # Check reference is valid
            assert "reference" in msg.value
            assert msg.value["reference"] == cfg["reference"]
            # Check operation
            assert exp == msg.value["$op"]
            if msg.value["$op"] == "raise":
                # Check managed object
                assert msg.value["managed_object"] == cfg["managed_object"]
                # Check timestamp
                assert "timestamp" in msg.value
                # Check labels
                assert msg.value["labels"] == cfg["labels"]
        del node


@pytest.mark.parametrize(
    "config,expected",
    [
        # No vars
        (None, None),
        # Empty list
        ({"vars": []}, None),
        # Fixed values
        (
            {"vars": [{"name": "x", "value": "test"}, {"name": "y", "value": "test!"}]},
            {"x": "test", "y": "test!", "ovalue": 1.0, "tvalue": 1.0, "node_id": "node"},
        ),
        # Templated values
        (
            {
                "vars": [
                    {"name": "x", "value": "{{x}}"},
                    {"name": "level", "value": "{{config.activation_level}}"},
                    {"name": "deactivation", "value": "{{config.deactivation_level}}"},
                    {
                        "name": "span",
                        "value": "{{config.activation_level - config.deactivation_level}}",
                    },
                ]
            },
            {
                "x": "1.0",
                "level": "1.0",
                "deactivation": "0.5",
                "span": "0.5",
                "ovalue": 1.0,
                "tvalue": 1.0,
                "node_id": "node",
            },
        ),
    ],
)
def test_alarm_vars(config, expected):
    default_cfg = {
        "reference": "test:1",
        "pool": "TEST",
        "partition": 3,
        "alarm_class": "Test",
        "managed_object": "777",
        "labels": ["l1", "l2"],
        "activation_level": 1.0,
        "deactivation_level": 0.5,
    }
    cfg = default_cfg.copy()
    if config:
        cfg.update(config)
    cdag = NodeCDAG("alarm", cfg)
    with publish_service() as svc:
        cdag.begin()
        cdag.activate("x", 1.0)
        messages = list(svc.iter_published())
        assert len(messages) == 1, "Lost message"
        msg = messages[0]
        if expected is None:
            assert "vars" in msg.value
            assert msg.value["vars"] == {
                "tvalue": default_cfg["activation_level"],
                "ovalue": 1.0,
                "node_id": "node",
            }
        else:
            assert "vars" in msg.value
            assert msg.value["vars"] == expected
        del cdag


@pytest.mark.parametrize(
    "config,values,expected,state",
    [
        # Default levels
        (
            {"thresholds": [{"value": 1.0}]},
            [0.0, 0.5, 0.99, 1.0, 1.5, 1.0, 0.99, 0.5, 0.0],
            [None, None, None, "raise", None, None, "clear", None, None],
            [False, False, False, True, True, True, False, False, False],
        ),
        # Test with specific operation
        (
            {"thresholds": [{"op": ">=", "value": 1.0}]},
            [0.0, 0.5, 0.99, 1.0, 1.5, 1.0, 0.99, 0.5, 0.0],
            [None, None, None, "raise", None, None, "clear", None, None],
            [False, False, False, True, True, True, False, False, False],
        ),
        (
            {"thresholds": [{"op": ">", "value": 1.0}]},
            [0.0, 0.5, 0.99, 1.0, 1.5, 1.4, 1.0, 0.99, 0.5, 0.0],
            [None, None, None, None, "raise", None, "clear", None, None, None],
            [False, False, False, False, True, True, False, False, False, False],
        ),
        (
            {"thresholds": [{"op": "<=", "value": 1.0}]},
            [1.5, 1.4, 1.0, 0.99, 0.5, 0.0, 0.5, 0.99, 1.0, 1.4, 1.5],
            [None, None, "raise", None, None, None, None, None, None, "clear", None],
            [False, False, True, True, True, True, True, True, True, False, False],
        ),
        (
            {"thresholds": [{"op": "<", "value": 1.0}]},
            [1.5, 1.4, 1.0, 0.99, 0.5, 0.0, 0.5, 0.99, 1.0, 1.4, 1.5],
            [None, None, None, "raise", None, None, None, None, "clear", None, None],
            [False, False, False, True, True, True, True, True, False, False, False],
        ),
        # Test without clean_value
        (
            {"thresholds": [{"op": ">=", "value": 10.0}]},
            [9.0, 10.0, 10.0, 10.0, 9.0],
            [None, "raise", None, None, "clear"],
            [False, True, True, True, False],
        ),
        (
            {"thresholds": [{"op": ">", "value": 10.0}]},
            [10.0, 11.0, 11.0, 11.0, 10.0],
            [None, "raise", None, None, "clear"],
            [False, True, True, True, False],
        ),
        (
            {"thresholds": [{"op": "<", "value": 10.0}]},
            [10.0, 9.0, 9.0, 9.0, 10.0],
            [None, "raise", None, None, "clear"],
            [False, True, True, True, False],
        ),
        (
            {"thresholds": [{"op": "<=", "value": 10.0}]},
            [11.0, 10.0, 10.0, 10.0, 11.0],
            [None, "raise", None, None, "clear"],
            [False, True, True, True, False],
        ),
        # Test with negative value (as attenuation in dBm)
        (
            {"thresholds": [{"op": ">=", "value": -15.0}]},
            [-15.5, -15.0, -15.0, -15.5, -15.5],
            [None, "raise", None, "clear", None],
            [False, True, True, False, False],
        ),
        (
            {"thresholds": [{"op": ">", "value": -15.0}]},
            [-15.0, -14.9, -14.8, -15.0, -15.1],
            [None, "raise", None, "clear", None],
            [False, True, True, False, False],
        ),
        (
            {"thresholds": [{"op": "<", "value": -15.0}]},
            [-15.0, -15.1, -15.2, -15.0, -14.9],
            [None, "raise", None, "clear", None],
            [False, True, True, False, False],
        ),
        (
            {"thresholds": [{"op": "<=", "value": -15.0}]},
            [-14.9, -15.0, -15.1, -14.9, -14.8],
            [None, "raise", None, "clear", None],
            [False, True, True, False, False],
        ),
        # Test with clean_value same as value
        (
            {"thresholds": [{"op": ">=", "value": 10.0, "clear_value": 10.0}]},
            [9.0, 10.0, 10.0, 10.0, 9.0],
            [None, "raise", None, None, "clear"],
            [False, True, True, True, False],
        ),
        (
            {"thresholds": [{"op": ">", "value": 10.0, "clear_value": 10.0}]},
            [10.0, 11.0, 11.0, 11.0, 10.0],
            [None, "raise", None, None, "clear"],
            [False, True, True, True, False],
        ),
        (
            {"thresholds": [{"op": "<", "value": 10.0, "clear_value": 10.0}]},
            [10.0, 9.0, 9.0, 9.0, 10.0],
            [None, "raise", None, None, "clear"],
            [False, True, True, True, False],
        ),
        (
            {"thresholds": [{"op": "<=", "value": 10.0, "clear_value": 10.0}]},
            [11.0, 10.0, 10.0, 10.0, 11.0],
            [None, "raise", None, None, "clear"],
            [False, True, True, True, False],
        ),
        # Test with clean_value
        (
            {"thresholds": [{"op": ">=", "value": 1.0, "clear_value": 0.5}]},
            [0.99, 1.0, 1.1, 1.4, 0.51, 0.5, 0.49],
            [None, "raise", None, None, None, None, "clear"],
            [False, True, True, True, True, True, False],
        ),
        (
            {"thresholds": [{"op": ">", "value": 1.0, "clear_value": 0.5}]},
            [1.0, 1.1, 1.4, 0.51, 0.5, 0.49],
            [None, "raise", None, None, "clear", None],
            [False, True, True, True, False, False],
        ),
        (
            {"thresholds": [{"op": "<=", "value": 1.0, "clear_value": 1.5}]},
            [1.4, 1.0, 0.99, 0.5, 0.99, 1.0, 1.4, 1.5, 1.51],
            [None, "raise", None, None, None, None, None, None, "clear"],
            [False, True, True, True, True, True, True, True, False],
        ),
        (
            {"thresholds": [{"op": "<", "value": 1.0, "clear_value": 1.5}]},
            [1.0, 0.99, 0.5, 0.99, 1.0, 1.4, 1.5, 1.51],
            [None, "raise", None, None, None, None, "clear", None],
            [False, True, True, True, True, True, False, False],
        ),
        # Hysteresis
        # (
        #     {"activation_level": 1.0, "deactivation_level": 0.5},
        #     [0.0, 0.5, 0.99, 1.0, 1.5, 1.0, 0.99, 0.5, 0.49, 0.2, 0.0],
        #     [None, None, None, "raise", None, None, None, None, "clear", None, None],
        #     [False, False, False, True, True, True, True, True, False, False, False],
        # ),
    ],
)
def test_threshold(config, values, expected, state):
    assert len(values) == len(expected), "Broken test"
    assert len(values) == len(state), "Broken test"
    default_cfg = {
        "reference": "test:1",
        "pool": "TEST",
        "partition": 3,
        "alarm_class": "Test",
        "managed_object": "777",
        "labels": ["l1", "l2"],
    }
    cfg = default_cfg.copy()
    cfg.update(config)
    cdag = NodeCDAG("threshold", cfg)
    node = cdag.get_node()
    with publish_service() as svc:
        for v, exp, st in zip(values, expected, state):
            cdag.begin()
            cdag.activate("x", v)
            # Check state change
            assert node.is_active() is st, "Invalid state"
            # Check published messages
            messages = list(svc.iter_published())
            if not messages:
                # No message sent
                assert exp is None, "Lost message"
                continue
            assert len(messages) == 1, "Multiple message sent"
            assert exp is not None, "Unexpected message sent"
            msg = messages[0]
            # Check $op is set
            assert "$op" in msg.value
            # Check reference is valid
            assert "reference" in msg.value
            assert msg.value["reference"] == cfg["reference"]
            # Check operation
            assert exp == msg.value["$op"]
            if msg.value["$op"] == "raise":
                # Check managed object
                assert msg.value["managed_object"] == cfg["managed_object"]
                # Check timestamp
                assert "timestamp" in msg.value
                # Check labels
                assert msg.value["labels"] == cfg["labels"]
