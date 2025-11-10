# ----------------------------------------------------------------------
# YAMLFactory tests
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


@pytest.mark.parametrize(("config", "out_state"), [(CONFIG, {"n04": {"value": 3.0}})])
def test_yaml_factory(config, out_state):
    # Empty graph with no state
    cdag = CDAG("test", {})
    # Apply config
    factory = YAMLCDAGFactory(cdag, CONFIG)
    factory.construct()
    # Compare final state with expected
    assert cdag.get_state() == out_state
