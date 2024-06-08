# ----------------------------------------------------------------------
# CDAG.to_dot() tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.cdag.graph import CDAG
from noc.core.cdag.factory.yaml import YAMLCDAGFactory


CONFIG = """
nodes:
- name: n01
  description: Value of 1
  type: value
  config:
    value: 1.0
- name: n02
  type: value
  description: Value of 2
  config:
    value: 2.0
- name: n03
  type: add
  description: Add values
  inputs:
  - name: x
    node: n01
  - name: y
    node: n02
- name: n04
  type: state
  inputs:
  - name: x
    node: n03
"""

DOT = r"""digraph {
  rankdir="LR";
  n00000 [label="n01\ntype: value\nvalue: 1.0", shape="cds"];
  n00001 [label="n02\ntype: value\nvalue: 2.0", shape="cds"];
  n00002 [label="n03\ntype: add", shape="box"];
  n00003 [label="n04\ntype: state", shape="doubleoctagon"];
  n00000 -> n00002 [label="x"];
  n00001 -> n00002 [label="y"];
  n00002 -> n00003 [label="x"];
}"""


def test_to_dot():
    cdag = CDAG("test", {})
    # Apply config
    factory = YAMLCDAGFactory(cdag, CONFIG)
    factory.construct()
    assert cdag.get_dot() == DOT


def test_duplicated_node():
    cdag = CDAG("test", {})
    cdag.add_node("n01", "none")
    with pytest.raises(ValueError):
        cdag.add_node("n01", "none")


def test_invalid_node_class():
    cdag = CDAG("test", {})
    with pytest.raises(ValueError):
        cdag.add_node("n01", "none!!!")


CONST_CONFIG = """
nodes:
- name: n01
  description: Value of 1
  type: value
  config:
    value: 1.0
- name: n02
  type: value
  description: Value of 2
  config:
    value: 2.0
- name: n03
  type: add
  description: Add values
  inputs:
  - name: x
    node: n01
  - name: y
    node: n02
- name: n04
  type: value
  description: Value of 3
  config:
    value: 3.0
- name: n05
  type: mul
  description: Multiply values
  inputs:
  - name: x
    node: n03
  - name: y
    node: n04
- name: measure
  type: none
  description: Measured result
  inputs:
  - name: x
    node: n05
"""


def test_const():
    cdag = CDAG("test", {})
    # Apply config
    factory = YAMLCDAGFactory(cdag, CONST_CONFIG)
    factory.construct()
    node = cdag.get_node("measure")
    assert node.is_const_input("x")
    assert node.const_inputs["x"] == 9.0
    tx = cdag.begin()
    inputs = tx.get_inputs(node)
    assert "x" in inputs
    assert inputs["x"] == 9.0
