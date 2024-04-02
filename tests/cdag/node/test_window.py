# ----------------------------------------------------------------------
# Test WindowNode
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.cdag.node.window import WindowNode, NS
from .util import NodeCDAG


@pytest.mark.parametrize(
    "op,config,measures,expected",
    [
        # nth
        ("nth", {}, [1, 2, 3, 4, 5], [None, 1, 2, 3, 4]),
        ("nth", {"n": 0}, [1, 2, 3, 4, 5], [1, 2, 3, 4, 5]),
        ("nth", {"n": 1}, [1, 2, 3, 4, 5], [None, 1, 2, 3, 4]),
        ("nth", {"n": 3}, [1, 2, 3, 4, 5], [None, None, None, 1, 2]),
        # percentile
        ("percentile", {"percentile": 50, "min_window": 0}, [1, 2, 3, 4, 5, 6], [1, 2, 2, 3, 3, 4]),
        (
            "percentile",
            {"percentile": 50, "min_window": 3},
            [1, 2, 3, 4, 5, 6],
            [None, None, 2, 3, 3, 4],
        ),
        # sumstep
        ("sumstep", {"direction": "inc"}, [1, 2, -1, 1, -1, 1], [0, 1, 1, 3, 3, 5]),
        (
            "sumstep",
            {"direction": "inc", "min_window": 3},
            [1, 2, -1, 1, -1, 1],
            [None, None, 1, 3, 3, 5],
        ),
        ("sumstep", {"direction": "dec"}, [1, 2, -1, 1, -1, 1], [0, 0, 3, 3, 5, 5]),
        ("sumstep", {"direction": "abs"}, [1, 2, -1, 1, -1, 1], [0, 1, 4, 6, 8, 10]),
        #
        ("expdecay", {"k": 1.0}, [10], [10]),
    ],
)
def test_window_node(op, config, measures, expected):
    state = {}
    cdag = NodeCDAG(op, config=config, state=state)
    for ms, exp in zip(measures, expected):
        cdag.begin()
        cdag.activate("x", ms)
        value = cdag.get_value()
        if exp is None:
            assert value is exp
        else:
            assert value == exp
        state = cdag.get_changed_state()
        assert state and ("node", op) in state


def get_steps(start, step, n):
    return [(start + i * step, i) for i in range(n)]


T0 = 1604992784000000000
W_SEQ = [(T0 + i * 10 * NS, i) for i in range(5)]


@pytest.mark.parametrize(
    "min_window,data,expected",
    [
        (1, [], False),
        (1, W_SEQ[:1], True),
        (2, W_SEQ[:1], False),
        (2, W_SEQ[:2], True),
        (3, W_SEQ[:2], False),
        (3, W_SEQ[:3], True),
        (3, W_SEQ[:3], True),
        (3, W_SEQ, True),
    ],
)
def test_window_filled_ticks(min_window, data, expected):
    def get_node():
        return WindowNode("n01", state=state, config={"type": "t", "min_window": min_window})

    state = {}
    for ts, value in data:
        node = get_node()
        node.push(ts, value)
        state = node.get_state().dict()
    node = get_node()
    assert node.is_filled_ticks() is expected


@pytest.mark.parametrize(
    "min_window,ts,data,expected",
    [
        (0, T0, [], False),
        (10, T0 + 9 * NS, W_SEQ[:1], False),
        (10, T0 + 11 * NS, W_SEQ[:1], True),
    ],
)
def test_window_filled_seconds(min_window, ts, data, expected):
    def get_node():
        return WindowNode("n01", state=state, config={"type": "s", "min_window": min_window})

    state = {}
    for t, value in data:
        node = get_node()
        node.push(t, value)
        state = node.get_state().dict()
    node = get_node()
    is_filled = node.is_filled_seconds(ts)
    assert is_filled is expected


@pytest.mark.parametrize(
    "max_window,data,expected",
    [
        (1, [], []),
        (1, W_SEQ[:1], W_SEQ[:1]),
        (1, W_SEQ[:2], W_SEQ[1:2]),
        (1, W_SEQ[:3], W_SEQ[2:3]),
        (2, W_SEQ[:3], W_SEQ[1:3]),
        (10, W_SEQ, W_SEQ),
    ],
)
def test_window_trim_ticks(max_window, data, expected):
    def get_node():
        return WindowNode("n01", state=state, config={"type": "t", "max_window": max_window})

    state = {}
    for t, value in data:
        node = get_node()
        node.push(t, value)
        state = node.get_state().dict()
    node = get_node()
    node.trim_ticks()
    state = node.get_state().dict()
    assert "timestamps" in state
    assert "values" in state
    expected_timestamps = [x[0] for x in expected]
    assert state["timestamps"] == expected_timestamps
    expected_values = [x[1] for x in expected]
    assert state["values"] == expected_values


@pytest.mark.parametrize(
    "max_window,data,expected",
    [
        (1, [], []),
        (1, W_SEQ[:1], W_SEQ[:1]),
        (1, W_SEQ[:2], W_SEQ[1:2]),
        (10, W_SEQ[:2], W_SEQ[:2]),
    ],
)
def test_window_trim_seconds(max_window, data, expected):
    def get_node():
        return WindowNode("n01", state=state, config={"type": "s", "max_window": max_window})

    state = {}
    for t, value in data:
        node = get_node()
        node.push(t, value)
        state = node.get_state().dict()
    node = get_node()
    node.trim_seconds(data[-1][0] if data else T0)
    state = node.get_state().dict()
    assert "timestamps" in state
    assert "values" in state
    expected_timestamps = [x[0] for x in expected]
    assert state["timestamps"] == expected_timestamps
    expected_values = [x[1] for x in expected]
    assert state["values"] == expected_values
