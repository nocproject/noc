# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# noc.core.mac unittests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest
# NOC modules
from noc.core.mac import MAC


def test_mac_colon():
    assert MAC("12:34:56:78:9a:bc") == "12:34:56:78:9A:BC"
    assert MAC("12:34:56:78:9A:BC") == "12:34:56:78:9A:BC"


def test_mac_colon_short():
    assert MAC("0:13:46:50:87:5") == "00:13:46:50:87:05"


def test_mac_nosep():
    assert MAC("aabbccddeeff") == "AA:BB:CC:DD:EE:FF"
    assert MAC("AABBCCDDEEFF") == "AA:BB:CC:DD:EE:FF"


def test_mac_int():
    assert MAC(0xAABBCCDDEEFF) == "AA:BB:CC:DD:EE:FF"


def test_mac_bin():
    assert MAC("\xaa\xbb\xcc\xdd\xee\xff") == "AA:BB:CC:DD:EE:FF"


def test_mac_cisco():
    assert MAC("1234.5678.9ABC") == "12:34:56:78:9A:BC"
    assert MAC("1234.5678.9abc") == "12:34:56:78:9A:BC"
    assert MAC("0112.3456.789a.bc") == "12:34:56:78:9A:BC"
    with pytest.raises(ValueError):
        MAC("1234.5678.9abc.def0")


def test_mac_dash1():
    assert MAC("123456-789abc") == "12:34:56:78:9A:BC"


def test_mac_dash3():
    assert MAC("aabb-ccdd-eeff") == "AA:BB:CC:DD:EE:FF"


def test_mac_dash5():
    assert MAC("12-34-56-78-9A-BC") == "12:34:56:78:9A:BC"
    with pytest.raises(ValueError):
        MAC("12-34-56-78-9A-BC-DE")
    with pytest.raises(ValueError):
        MAC("AB-CD-EF-GH-HJ-KL")


def test_mac_str_op():
    assert MAC("AABBCCDDEEFF") + " -- " + MAC("0011.2233.4455") == "AA:BB:CC:DD:EE:FF -- 00:11:22:33:44:55"


def test_mac_to_cisco():
    assert MAC("AA:BB:CC:DD:EE:FF").to_cisco() == "aabb.ccdd.eeff"


def test_mac_shift():
    assert MAC("AA:BB:CC:DD:EE:FF").shift(0) == "AA:BB:CC:DD:EE:FF"
    assert MAC("AA:BB:CC:DD:EE:FF").shift(1) == "AA:BB:CC:DD:EF:00"
    assert MAC("AA:BB:CC:DD:EE:FF").shift(256) == "AA:BB:CC:DD:EF:FF"
    assert MAC("AA:BB:CC:DD:EE:FF").shift(257) == "AA:BB:CC:DD:F0:00"
    assert MAC("AA:BB:CC:DD:EE:FF").shift(4096) == "AA:BB:CC:DD:FE:FF"


def test_long():
    assert long(MAC("AA:BB:CC:DD:EE:FF")) == 0xAABBCCDDEEFF


def test_int():
    assert int(MAC("AA:BB:CC:DD:EE:FF")) == 0xAABBCCDDEEFF


@pytest.mark.parametrize("value", [
    # VRRP virtual
    "00:00:5E:00:01:01",
    "00:00:5E:00:01:02",
    # Plain MAC
    "AC:DE:48:00:01:02",
    "78:4F:43:01:02:53"
])
def test_unicast(value):
    assert MAC(value).is_multicast is False


@pytest.mark.parametrize("value", [
    # CDP
    "01:00:0C:CC:CC:CC",
    # LLDP
    "01:80:C2:00:00:00",
    "01:80:C2:00:00:03",
    "01:80:C2:00:00:0E"
])
def test_multicast(value):
    assert MAC(value).is_multicast is True
