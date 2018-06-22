# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# noc.lib.validatiors test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party packages
import pytest
# NOC modules
from noc.lib.validators import (
    is_int, is_float, is_asn, is_ipv4, is_ipv6, is_ipv4_prefix,
    is_ipv6_prefix, is_prefix, is_as_set, is_fqdn, is_re, is_vlan,
    is_mac, is_rd, is_oid, is_extension, is_email, is_uuid, is_mimetype,
    is_objectid, generic_validator, ValidationError
)


def test_is_int():
    assert is_int(10) is True
    assert is_int("10") is True
    assert is_int("Ten") is False
    assert is_int(None) is False


def test_is_float():
    assert is_float(10) is True
    assert is_float(10.2) is True
    assert is_float("10.2") is True
    assert is_float("Ten") is False
    assert is_float(None) is False


def test_is_asn():
    assert is_asn(100) is True
    assert is_asn(100000) is True
    assert is_asn(-1) is False


def test_is_ipv4():
    assert is_ipv4("192.168.0.1") is True
    assert is_ipv4("192.168.0") is False
    assert is_ipv4("192.168.0.1.1") is False
    assert is_ipv4("192.168.1.256") is False
    assert is_ipv4("192.168.a.250") is False


def test_is_ipv6():
    assert is_ipv6("::") is True
    assert is_ipv6("::1") is True
    assert is_ipv6("2001:db8::") is True
    assert is_ipv6("2001:db8:0000:0000:6232:6400::") is True
    assert is_ipv6("::ffff:192.168.0.1") is True
    assert is_ipv6("::ffff:192.168.0.256") is False
    assert is_ipv6("fe80::226:b0ff:fef7:c48c") is True
    assert is_ipv6("0:1:2:3:4:5:6:7:8") is False
    assert is_ipv6("0:1:2") is False
    assert is_ipv6("::g") is False
    assert is_ipv6("100:0:") is False
    assert is_ipv6("2a00:1118:f00f:fffe:c143:3284:1000::") is True
    assert is_ipv6("1::2:3:4:5:6:7:8:9") is False


def test_is_ipv4_prefix():
    assert is_ipv4_prefix("192.168.0.0") is False
    assert is_ipv4_prefix("192.168.0.0/16") is True
    assert is_ipv4_prefix("192.168.256.0/24") is False
    assert is_ipv4_prefix("192.168.0.0/g") is False
    assert is_ipv4_prefix("192.168.0.0/-1") is False
    assert is_ipv4_prefix("192.168.0.0/33") is False


def test_is_ipv6_prefix():
    assert is_ipv6_prefix("1::/32") is True
    assert is_ipv6_prefix("1::/-1") is False
    assert is_ipv6_prefix("1::/129") is False
    assert is_ipv6_prefix("1::/1/2") is False
    assert is_ipv6_prefix("1::/g") is False
    assert is_ipv6_prefix("192.168.0.0/32") is False


def test_is_prefix():
    assert is_prefix("192.168.0.0/16") is True
    assert is_prefix("1::/32") is True


def test_is_rd():
    # Special case RD: 0:0
    assert is_rd("0:0") is True
    # Type 0 RD: <2byte ASN> : <ID>
    assert is_rd("100:10") is True
    assert is_rd("100:0") is True
    assert is_rd("100:4294967295") is True
    assert is_rd("0:-10") is False
    assert is_rd("0:4294967296") is False
    # Type 1 RD: <IPv4> : <ID>
    assert is_rd("10.10.10.10:0") is True
    assert is_rd("10.10.10.10:65535") is True
    assert is_rd("10.10.10.10:-1") is False
    assert is_rd("10.10.10.10:65536") is False
    # Type 2 RD: <4byte ASN> : <ID>
    assert is_rd("100000:0") is True
    assert is_rd("100000:65535") is True
    # Error handling
    assert is_rd("100000:-1") is False
    assert is_rd("100000:65536") is False
    assert is_rd("10:20:30") is False
    assert is_rd("100:b") is False


def test_is_as_set():
    assert is_as_set("AS-TEST") is True
    assert is_as_set("AS100") is False


def test_is_fqdn():
    assert is_fqdn("test.example.com") is True
    assert is_fqdn("test") is False


def test_is_re():
    assert is_re("1{1,2}") is True
    assert is_re("1[") is False


def test_is_vlan():
    assert is_vlan(1) is True
    assert is_vlan(-1) is False
    assert is_vlan(4095) is True
    assert is_vlan(4096) is False
    assert is_vlan("g") is False


def test_is_mac():
    assert is_mac("1234.5678.9ABC") is True
    assert is_mac("1234.5678.9abc") is True
    assert is_mac("0112.3456.789a.bc") is True
    assert is_mac("1234.5678.9abc.def0") is False
    assert is_mac("12:34:56:78:9A:BC") is True
    assert is_mac("12-34-56-78-9A-BC") is True
    assert is_mac("0:13:46:50:87:5") is True
    assert is_mac("123456-789abc") is True
    assert is_mac("12-34-56-78-9A-BC-DE") is False
    assert is_mac("AB-CD-EF-GH-HJ-KL") is False
    assert is_mac("aabb-ccdd-eeff") is True
    assert is_mac("aabbccddeeff") is True
    assert is_mac("AABBCCDDEEFF") is True
    assert is_mac("\\xa8\\xf9K\\x80\\xb4\\xc0") is False
    assert is_mac(None) is False
    assert is_mac("123") is False

def test_is_email():
    assert is_email("test@example.com") is True
    assert is_email("test") is False


def test_is_oid():
    assert is_oid("1.3.6.1.6.3.1.1.4.1.0") is True
    assert is_oid("1.3.6.1.6.3.1.1.4.a.1.0") is False


def test_is_extension():
    assert is_extension(".txt") is True
    assert is_extension("txt") is False


def test_is_mimetype():
    assert is_mimetype("application/octet-stream") is True
    assert is_mimetype("application") is False


def test_is_uuid():
    assert is_uuid("689d99b5-419a-4411-a904-70366c8e5584") is True
    assert is_uuid("689d99b5-419a-4411-a904-70366c8e5584x") is False


def test_is_objectid():
    assert is_objectid("5b2d0cba4575cf01ead6aa89") is True


def test_generic_validator():
    v = generic_validator(is_int, "invalid int")
    assert v(6) == 6
    with pytest.raises(ValidationError):
        v("g")
