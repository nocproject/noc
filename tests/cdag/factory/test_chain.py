# ----------------------------------------------------------------------
# Test factory chain
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.cdag.graph import CDAG
from noc.core.cdag.factory.yaml import YAMLCDAGFactory


CONFIG1 = """
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
"""
CONFIG2 = """
nodes:
- name: n03
  type: add
  description: Add values
  inputs:
  - name: x
    node: n01
  - name: y
    node: n02
"""
CONFIG3 = """
nodes:
- name: n04
  type: state
  inputs:
  - name: x
    node: n03
"""


@pytest.mark.parametrize(
    ("configs", "out_state"), [([CONFIG1, CONFIG2, CONFIG3], {"n04": {"value": 3.0}})]
)
def test_factory_chain(configs, out_state):
    # Empty graph with no state
    cdag = CDAG("test", {})
    # Apply config
    for cfg in configs:
        factory = YAMLCDAGFactory(cdag, cfg)
        factory.construct()
    # Compare final state with expected
    assert cdag.get_state() == out_state


NS_CONFIG1 = """
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
"""
NS_CONFIG2 = """
nodes:
- name: n03
  type: add
  description: Add values
  inputs:
  - name: x
    node: ns1::n01
  - name: y
    node: ns1::n02
"""
NS_CONFIG3 = """
nodes:
- name: n04
  type: state
  inputs:
  - name: x
    node: "{{src}}"
"""


@pytest.mark.parametrize(
    ("ctx", "configs", "out_state"),
    [
        (
            {"src": "ns2::n03"},
            [("ns1", NS_CONFIG1), ("ns2", NS_CONFIG2), ("ns3", NS_CONFIG3)],
            {"ns3::n04": {"value": 3.0}},
        )
    ],
)
def test_factory_ns_chain(ctx, configs, out_state):
    # Empty graph with no state
    cdag = CDAG("test", {})
    # Apply config
    for ns, cfg in configs:
        factory = YAMLCDAGFactory(cdag, cfg, ctx, ns)
        factory.construct()
    # Compare final state with expected
    assert cdag.get_state() == out_state
