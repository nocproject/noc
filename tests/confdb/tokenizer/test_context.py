# ----------------------------------------------------------------------
# Test context tokenizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.confdb.tokenizer.context import ContextTokenizer
from noc.core.confdb.syntax.patterns import ANY


# Raisecom-like
CFG1 = """clock timezone + 3 0
terminal page-break disable
interface port 1
switchport access vlan 3009
switchport access egress-allowed vlan 90
ip igmp filter 10
ip igmp max-groups 6
mvr type receiver
mvr immediate
lldp disable
spanning-tree disable
switchport port-security maximum 2
!
interface port 2
switchport access vlan 3010
switchport access egress-allowed vlan 90
ip igmp filter 10
ip igmp max-groups 6
mvr type receiver
mvr immediate
lldp disable
spanning-tree disable
switchport port-security maximum 2
!
interface ip 0
ip vlan 126
ip address 172.16.0.1 255.255.254.0 126
"""

TOKENS1 = [
    ("clock", "timezone", "+", "3", "0"),
    ("terminal", "page-break", "disable"),
    ("interface", "port", "1"),
    ("interface", "port", "1", "switchport", "access", "vlan", "3009"),
    ("interface", "port", "1", "switchport", "access", "egress-allowed", "vlan", "90"),
    ("interface", "port", "1", "ip", "igmp", "filter", "10"),
    ("interface", "port", "1", "ip", "igmp", "max-groups", "6"),
    ("interface", "port", "1", "mvr", "type", "receiver"),
    ("interface", "port", "1", "mvr", "immediate"),
    ("interface", "port", "1", "lldp", "disable"),
    ("interface", "port", "1", "spanning-tree", "disable"),
    ("interface", "port", "1", "switchport", "port-security", "maximum", "2"),
    ("interface", "port", "2"),
    ("interface", "port", "2", "switchport", "access", "vlan", "3010"),
    ("interface", "port", "2", "switchport", "access", "egress-allowed", "vlan", "90"),
    ("interface", "port", "2", "ip", "igmp", "filter", "10"),
    ("interface", "port", "2", "ip", "igmp", "max-groups", "6"),
    ("interface", "port", "2", "mvr", "type", "receiver"),
    ("interface", "port", "2", "mvr", "immediate"),
    ("interface", "port", "2", "lldp", "disable"),
    ("interface", "port", "2", "spanning-tree", "disable"),
    ("interface", "port", "2", "switchport", "port-security", "maximum", "2"),
    ("interface", "ip", "0"),
    ("interface", "ip", "0", "ip", "vlan", "126"),
    ("interface", "ip", "0", "ip", "address", "172.16.0.1", "255.255.254.0", "126"),
]

# Alstec-like
CFG2 = """network mgmt_vlan 999
vlan database
vlan 102,999,2361-2555,4001
exit
policy-map qos_set in
class management
assign-queue 7
exit
class realtime
assign-queue 5
exit
exit
interface 0/2
vlan pvid 2361
vlan participation include 2361,4001
set igmp
exit
interface 0/3
vlan pvid 2362
vlan participation include 2362,4001
set igmp
exit
"""

TOKENS2 = [
    ("network", "mgmt_vlan", "999"),
    ("vlan", "database"),
    ("vlan", "database", "vlan", "102,999,2361-2555,4001"),
    ("policy-map", "qos_set", "in"),
    ("policy-map", "qos_set", "in", "class", "management"),
    ("policy-map", "qos_set", "in", "class", "management", "assign-queue", "7"),
    ("policy-map", "qos_set", "in", "class", "realtime"),
    ("policy-map", "qos_set", "in", "class", "realtime", "assign-queue", "5"),
    ("interface", "0/2"),
    ("interface", "0/2", "vlan", "pvid", "2361"),
    ("interface", "0/2", "vlan", "participation", "include", "2361,4001"),
    ("interface", "0/2", "set", "igmp"),
    ("interface", "0/3"),
    ("interface", "0/3", "vlan", "pvid", "2362"),
    ("interface", "0/3", "vlan", "participation", "include", "2362,4001"),
    ("interface", "0/3", "set", "igmp"),
]


@pytest.mark.parametrize(
    ("input", "config", "expected"),
    [
        # Raisecom
        (CFG1, {"contexts": [["interface", ANY, ANY]], "end_of_context": "!"}, TOKENS1),
        # Asltec
        (
            CFG2,
            {
                "contexts": [
                    ["vlan", "database"],
                    ["policy-map", ANY, ANY],
                    ["policy-map", ANY, ANY, "class", ANY],
                    ["interface", ANY],
                ],
                "end_of_context": "exit",
            },
            TOKENS2,
        ),
    ],
)
def test_tokenizer(input, config, expected):
    tokenizer = ContextTokenizer(input, **config)
    assert list(tokenizer) == expected
