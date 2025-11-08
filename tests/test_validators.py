# ----------------------------------------------------------------------
# noc.lib.validatiors test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party packages
import pytest

# NOC modules
from noc.core.validators import (
    is_int,
    is_float,
    is_asn,
    is_ipv4,
    is_ipv6,
    is_ipv4_prefix,
    is_ipv6_prefix,
    is_prefix,
    is_as_set,
    is_fqdn,
    is_re,
    is_vlan,
    is_mac,
    is_rd,
    is_oid,
    is_extension,
    is_email,
    is_uuid,
    is_mimetype,
    is_objectid,
    generic_validator,
    ValidationError,
)


@pytest.mark.parametrize(
    ("raw", "expected"), [(10, True), ("10", True), ("Ten", False), (None, False)]
)
def test_is_int(raw, expected):
    assert is_int(raw) is expected


@pytest.mark.parametrize(
    ("raw", "expected"), [(10, True), (10.2, True), ("10.2", True), ("Ten", False), (None, False)]
)
def test_is_float(raw, expected):
    assert is_float(raw) is expected


@pytest.mark.parametrize(("raw", "expected"), [(100, True), (100000, True), (-1, False)])
def test_is_asn(raw, expected):
    assert is_asn(raw) is expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("192.168.0.1", True),
        ("192.168.0", False),
        ("192.168.0.1.1", False),
        ("192.168.1.256", False),
        ("192.168.a.250", False),
    ],
)
def test_is_ipv4(raw, expected):
    assert is_ipv4(raw) is expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("::", True),
        ("::1", True),
        ("2001:db8::", True),
        ("2001:db8:0000:0000:6232:6400::", True),
        ("::ffff:192.168.0.1", True),
        ("::ffff:192.168.0.256", False),
        ("fe80::226:b0ff:fef7:c48c", True),
        ("0:1:2:3:4:5:6:7:8", False),
        ("0:1:2", False),
        ("::g", False),
        ("100:0:", False),
        ("2a00:1118:f00f:fffe:c143:3284:1000::", True),
        ("1::2:3:4:5:6:7:8:9", False),
    ],
)
def test_is_ipv6(raw, expected):
    assert is_ipv6(raw) is expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("192.168.0.0", False),
        ("192.168.0.0/16", True),
        ("192.168.256.0/24", False),
        ("192.168.0.0/g", False),
        ("192.168.0.0/-1", False),
        ("192.168.0.0/33", False),
    ],
)
def test_is_ipv4_prefix(raw, expected):
    assert is_ipv4_prefix(raw) is expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("1::/32", True),
        ("1::/-1", False),
        ("1::/129", False),
        ("1::/1/2", False),
        ("1::/g", False),
        ("192.168.0.0/32", False),
    ],
)
def test_is_ipv6_prefix(raw, expected):
    assert is_ipv6_prefix(raw) is expected


@pytest.mark.parametrize(("raw", "expected"), [("192.168.0.0/16", True), ("1::/32", True)])
def test_is_prefix(raw, expected):
    assert is_prefix(raw) is expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        # Special case RD: 0:0
        ("0:0", True),
        # Type 0 RD: <2byte ASN> : <ID>
        ("100:10", True),
        ("100:0", True),
        ("100:4294967295", True),
        ("0:-10", False),
        ("0:4294967296", False),
        # Type 1 RD: <IPv4> : <ID>
        ("10.10.10.10:0", True),
        ("10.10.10.10:65535", True),
        ("10.10.10.10:-1", False),
        ("10.10.10.10:65536", False),
        # Type 2 RD: <4byte ASN> : <ID>
        ("100000:0", True),
        ("100000:65535", True),
        # Error handling
        ("100000:-1", False),
        ("100000:65536", False),
        ("10:20:30", False),
        ("100:b", False),
    ],
)
def test_is_rd(raw, expected):
    assert is_rd(raw) is expected


@pytest.mark.parametrize(("raw", "expected"), [("AS-TEST", True), ("AS100", False)])
def test_is_as_set(raw, expected):
    assert is_as_set(raw) is expected


@pytest.mark.parametrize(("raw", "expected"), [("test.example.com", True), ("test", False)])
def test_is_fqdn(raw, expected):
    assert is_fqdn(raw) is expected


@pytest.mark.parametrize(("raw", "expected"), [("1{1,2}", True), ("1[", False)])
def test_is_re(raw, expected):
    assert is_re(raw) is expected


@pytest.mark.parametrize(
    ("raw", "expected"), [(1, True), (-1, False), (4095, True), (4096, False), ("g", False)]
)
def test_is_vlan(raw, expected):
    assert is_vlan(raw) is expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("1234.5678.9ABC", True),
        ("1234.5678.9abc", True),
        ("0112.3456.789a.bc", True),
        ("1234.5678.9abc.def0", False),
        ("12:34:56:78:9A:BC", True),
        ("12-34-56-78-9A-BC", True),
        ("0:13:46:50:87:5", True),
        ("123456-789abc", True),
        ("12-34-56-78-9A-BC-DE", False),
        ("AB-CD-EF-GH-HJ-KL", False),
        ("aabb-ccdd-eeff", True),
        ("aabbccddeeff", True),
        ("AABBCCDDEEFF", True),
        ("\\xa8\\xf9K\\x80\\xb4\\xc0", False),
        (None, False),
        ("123", False),
    ],
)
def test_is_mac(raw, expected):
    assert is_mac(raw) is expected


@pytest.mark.parametrize(("raw", "expected"), [("test@example.com", True), ("test", False)])
def test_is_email(raw, expected):
    assert is_email(raw) is expected


@pytest.mark.parametrize(
    ("raw", "expected"), [("1.3.6.1.6.3.1.1.4.1.0", True), ("1.3.6.1.6.3.1.1.4.a.1.0", False)]
)
def test_is_oid(raw, expected):
    assert is_oid(raw) is expected


@pytest.mark.parametrize(("raw", "expected"), [(".txt", True), ("txt", False)])
def test_is_extension(raw, expected):
    assert is_extension(raw) is expected


@pytest.mark.parametrize(
    ("raw", "expected"), [("application/octet-stream", True), ("application", False)]
)
def test_is_mimetype(raw, expected):
    assert is_mimetype(raw) is expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("689d99b5-419a-4411-a904-70366c8e5584", True),
        ("689d99b5-419a-4411-a904-70366c8e5584x", False),
    ],
)
def test_is_uuid(raw, expected):
    assert is_uuid(raw) is expected


@pytest.mark.parametrize(("raw", "expected"), [("5b2d0cba4575cf01ead6aa89", True)])
def test_is_objectid(raw, expected):
    assert is_objectid(raw) is expected


def test_generic_validator():
    v = generic_validator(is_int, "invalid int")
    assert v(6) == 6
    with pytest.raises(ValidationError):
        v("g")
