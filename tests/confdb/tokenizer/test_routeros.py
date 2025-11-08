# ----------------------------------------------------------------------
# Test routeros tokenizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.confdb.tokenizer.routeros import RouterOSTokenizer

CFG1 = """/some single-line context
/interface ethernet
set [ find default-name=ether4 ] name=TV
set [ find default-name=ether1 ] mac-address=00:00:DE:AD:BE:EF name=WAN speed=100Mbps
set [ find default-name=ether2 ] name=Disk
set [ find default-name=ether3 ] name=eth3 speed=100Mbps
set [ find default-name=ether5 ] name=eth5 speed=100Mbps
/interface bridge
add admin-mac=00:11:22:33:44:55 auto-mac=no fast-forward=no mtu=1500 name=bridge1 protocol-mode=none
/ip dhcp-client
add comment="default configuration" dhcp-options=hostname,clientid disabled=no interface=WAN
/system identity
set name=rb
/system logging action
set 0 memory-lines=100
set 1 disk-lines-per-file=100
"""

TOKENS1 = [
    ("/some", "single-line", "context"),
    ("/interface", "ethernet", "ether4", "name", "TV"),
    ("/interface", "ethernet", "ether1", "mac-address", "00:00:DE:AD:BE:EF"),
    ("/interface", "ethernet", "ether1", "name", "WAN"),
    ("/interface", "ethernet", "ether1", "speed", "100Mbps"),
    ("/interface", "ethernet", "ether2", "name", "Disk"),
    ("/interface", "ethernet", "ether3", "name", "eth3"),
    ("/interface", "ethernet", "ether3", "speed", "100Mbps"),
    ("/interface", "ethernet", "ether5", "name", "eth5"),
    ("/interface", "ethernet", "ether5", "speed", "100Mbps"),
    ("/interface", "bridge", "0", "admin-mac", "00:11:22:33:44:55"),
    ("/interface", "bridge", "0", "auto-mac", "no"),
    ("/interface", "bridge", "0", "fast-forward", "no"),
    ("/interface", "bridge", "0", "mtu", "1500"),
    ("/interface", "bridge", "0", "name", "bridge1"),
    ("/interface", "bridge", "0", "protocol-mode", "none"),
    ("/ip", "dhcp-client", "0", "comment", "default configuration"),
    ("/ip", "dhcp-client", "0", "dhcp-options", "hostname,clientid"),
    ("/ip", "dhcp-client", "0", "disabled", "no"),
    ("/ip", "dhcp-client", "0", "interface", "WAN"),
    ("/system", "identity", "name", "rb"),
    ("/system", "logging", "action", "0", "memory-lines", "100"),
    ("/system", "logging", "action", "1", "disk-lines-per-file", "100"),
]
CFG2 = """/ip service
set telnet disabled=yes
set ftp disabled=yes
set www disabled=yes
set ssh port=22000
set api disabled=yes
set winbox address=192.168.16.0/24,192.168.61.0/24
set api-ssl disabled=yes
"""

TOKENS2 = [
    ("/ip", "service", "telnet", "disabled", "yes"),
    ("/ip", "service", "ftp", "disabled", "yes"),
    ("/ip", "service", "www", "disabled", "yes"),
    ("/ip", "service", "ssh", "port", "22000"),
    ("/ip", "service", "api", "disabled", "yes"),
    ("/ip", "service", "winbox", "address", "192.168.16.0/24,192.168.61.0/24"),
    ("/ip", "service", "api-ssl", "disabled", "yes"),
]


@pytest.mark.parametrize(
    ("input", "config", "expected"), [(CFG1, {}, TOKENS1), (CFG2, {}, TOKENS2)]
)
def test_tokenizer(input, config, expected):
    tokenizer = RouterOSTokenizer(input, **config)
    assert list(tokenizer) == expected
