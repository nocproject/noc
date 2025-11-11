# ----------------------------------------------------------------------
# noc.core.vlanmap test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.vlanmap import process_vlan_map, process_chain


@pytest.mark.parametrize(
    ("input", "expected", "rules"),
    [
        # >>> Ingress processing
        # Untagged vlan 10
        ([], [10], [{"op": "push", "vlan": 10}]),
        # Tagged vlan 10
        ([10], [10], []),
        # Push outer vlan 20
        ([10], [20, 10], [{"op": "push", "vlan": 20}]),
        # Rewrite inner vlan 10 to 20
        ([10], [20], [{"op": "swap", "vlan": 20}]),
        # Rewrite outer vlan 20 to 30
        ([20, 10], [30, 10], [{"op": "swap", "vlan": 30}]),
        # Pop inner vlan 10
        ([20, 10], [20], [{"op": "pop"}, {"op": "swap"}]),
        # Rewrite inner vlan 10 to 30
        (
            [20, 10],
            [20, 30],
            [{"op": "pop"}, {"op": "swap", "vlan": 30}, {"op": "drop"}, {"op": "push"}],
        ),
        # >>> Egress processing
        # Untagged vlan 10
        ([10], [], [{"op": "pop"}]),
        # Pop outer vlan 20
        ([20, 10], [10], [{"op": "pop"}]),
        # Pop outer vlan 10, rewrite inner vlan 10 to 30
        ([20, 10], [30], [{"op": "pop"}, {"op": "swap", "vlan": 30}]),
    ],
)
def test_vlan_map(input, expected, rules):
    output = process_vlan_map(input, rules)
    assert output == expected


@pytest.mark.parametrize(
    ("input", "expected", "chain"),
    [
        # untagged vlan 10 -- untagged vlan 10
        (
            [],  # Untagged
            [],  # Untagged
            [
                [{"op": "push", "vlan": 10}],  # Ingress 1. Add VLAN 10 to internal bridge
                [{"op": "pop"}],  # Egress 1. Pop VLAN tag
            ],
        ),
        # untagged vlan 10 -- tagged
        (
            [],  # Untagged
            [10],  # Tagged vlan 10
            [
                [{"op": "push", "vlan": 10}],  # Ingress 1. Add VLAN 10 to internal bridge
                [],  # Egress 1
            ],
        ),
        # (untagged vlan 10 -- tagged) -- ( tagged, untagged vlan 10)
        (
            [],  # Untagged
            [],  # Tagged vlan 10
            [
                # 1st
                [{"op": "push", "vlan": 10}],  # Ingress 1. Add VLAN 10 to internal bridge
                [],  # Egress 1
                # 2nd
                [],  # Ingress 2, pass vlan 10 to internal bridge
                [{"op": "pop"}],  # Egress 2, pop vlan tag
            ],
        ),
        # (untagged vlan 10 -- tagged) -- (tagged, tagged) -- (add outer vlan 20, q-in-q)
        (
            [],  # Untagged
            [20, 10],  # Q-in-Q
            # 1st
            [
                [{"op": "push", "vlan": 10}],  # Ingress 1. Add VLAN 10 to internal bridge
                [],  # Egress 1
                # 2nd
                [],
                [],
                # 3rd
                [{"op": "push", "vlan": 20}],
                [],
            ],
        ),
    ],
)
def test_process_chain(input, expected, chain):
    output = process_chain(input, chain)
    assert output == expected
