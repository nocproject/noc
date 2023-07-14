# ----------------------------------------------------------------------
# subgraph node test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from .util import NodeCDAG

# n * x + y
SG_CONFIG = """
nodes:
# Config is mapped outside
- name: n
  description: N, mapped outside
  type: value
# n * x
# x is external
- name: nx
  type: mul
  description: n * x
  inputs:
  - name: y
    node: n
# (n*x) + (y)
# y is external
- name: plus
  type: add
  description: add nx and y
  inputs:
  - name: x
    node: nx
- name: state
  type: state
  inputs:
  - name: x
    node: plus
"""

CONFIG = {
    "cdag": SG_CONFIG,
    "inputs": [
        {"public_name": "x", "node": "nx", "name": "x"},
        {"public_name": "y", "node": "plus", "name": "y"},
    ],
    "output": "state",
    "config": [{"name": "n", "node": "n", "param": "value"}],
    "n": 2,
}


def test_inputs():
    node = NodeCDAG("subgraph", config=CONFIG).get_node()
    inputs = set(node.iter_inputs())
    assert inputs == {"x", "y"}


def test_config():
    node = NodeCDAG("subgraph", config=CONFIG).get_node()
    vnode = node.cdag.get_node("n")
    assert vnode.config.value == 2


@pytest.mark.parametrize(
    "x,y,expected",
    [(0, 0, 0), (1, 0, 2), (0, 1, 1), (2, 1, 5)],
)
def test_subgraph_node(x, y, expected):
    cdag = NodeCDAG("subgraph", config=CONFIG)
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
    state = cdag.get_changed_state()[("node", "subgraph")]
    print(state)
    assert state["state"][("state", "state")] == {"value": expected}
