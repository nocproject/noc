# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# noc.core.snmp.ber tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.snmp.ber import BEREncoder, BERDecoder


@pytest.mark.parametrize(
    "raw, value",
    [
        ("", 0),
        ("\x00", 0),
        ("\x01", 1),
        ("\x7f", 127),
        ("\x00\x80", 128),
        ("\x01\x00", 256),
        ("\x80", -128),
        ("\xff\x7f", -129),
    ],
)
def test_decode_int(raw, value):
    decoder = BERDecoder()
    assert decoder.parse_int(raw) == value


@pytest.mark.parametrize(
    "raw, value",
    [
        ("@", float("+inf")),
        ("A", float("-inf")),
        ("\x031E+0", float("1")),
        ("\x0315E-1", float("1.5")),
    ],
)
def test_decode_real(raw, value):
    decoder = BERDecoder()
    assert decoder.parse_real(raw) == value


@pytest.mark.parametrize("raw, value", [("B", float("nan")), ("C", float("-0"))])
def test_decode_real_error(raw, value):
    decoder = BERDecoder()
    with pytest.raises(Exception):
        assert decoder.parse_real(raw) == value


@pytest.mark.xfail()
def test_decode_p_bitstring():
    raise NotImplementedError()


@pytest.mark.parametrize("raw, value", [("test", "test"), ("public", "public"), ("", "")])
def test_decode_p_octetstring(raw, value):
    decoder = BERDecoder()
    assert decoder.parse_p_octetstring(raw) == value


@pytest.mark.xfail()
def test_decode_p_t61_string():
    raise NotImplementedError()


@pytest.mark.xfail()
def test_decode_c_octetstring():
    raise NotImplementedError()


@pytest.mark.xfail()
def test_decode_c_t61_string():
    raise NotImplementedError()


@pytest.mark.parametrize("raw", ["\x00"])
def test_decode_null(raw):
    decoder = BERDecoder()
    assert decoder.parse_null(raw) is None


@pytest.mark.xfail()
def test_decode_a_ipaddress():
    raise NotImplementedError()


@pytest.mark.parametrize("raw, value", [("+\x06\x01\x02\x01\x01\x05\x00", "1.3.6.1.2.1.1.5.0")])
def test_decode_p_oid(raw, value):
    decoder = BERDecoder()
    assert decoder.parse_p_oid(raw) == value


@pytest.mark.xfail()
def test_decode_compressed_oid():
    raise NotImplementedError()


@pytest.mark.xfail()
def test_decode_sequence():
    raise NotImplementedError()


@pytest.mark.xfail()
def test_decode_implicit():
    raise NotImplementedError()


@pytest.mark.xfail()
def test_decode_set():
    raise NotImplementedError()


@pytest.mark.xfail()
def test_decode_utctime():
    raise NotImplementedError()


@pytest.mark.parametrize(
    "raw,value",
    [
        ("\x9f\x78\x04\x42\xf6\x00\x00", 123.0),
        # Opaque
        ("\x44\x07\x9f\x78\x04\x42\xf6\x00\x00", 123.0),
    ],
)
def test_decode_float(raw, value):
    decoder = BERDecoder()
    assert decoder.parse_tlv(raw)[0] == value


@pytest.mark.parametrize(
    "raw,value",
    [
        ("\x9f\x79\x08\x40\x5e\xc0\x00\x00\x00\x00\x00", 123.0),
        # Opaque
        ("\x44\x0b\x9f\x79\x08\x40\x5e\xc0\x00\x00\x00\x00\x00", 123.0),
    ],
)
def test_decode_double(raw, value):
    decoder = BERDecoder()
    assert decoder.parse_tlv(raw)[0] == value


@pytest.mark.parametrize("raw,value", [("\x44\x81\x06\x04\x04test", "test")])
def test_decode_opaque(raw, value):
    decoder = BERDecoder()
    assert decoder.parse_tlv(raw)[0] == value


@pytest.mark.xfail()
def test_encode_tlv():
    raise NotImplementedError()


@pytest.mark.parametrize(
    "raw, value", [("test", "\x04\x04test"), ("public", "\x04\x06public"), ("", "\x04\x00")]
)
def test_encode_octet_string(raw, value):
    encoder = BEREncoder()
    assert encoder.encode_octet_string(raw) == value


@pytest.mark.xfail()
def test_encode_sequence():
    raise NotImplementedError()


@pytest.mark.xfail()
def test_encode_choice():
    raise NotImplementedError()


@pytest.mark.parametrize(
    "value,raw",
    [
        (0, "\x02\x01\x00"),
        (1, "\x02\x01\x01"),
        (127, "\x02\x01\x7f"),
        (128, "\x02\x02\x00\x80"),
        (256, "\x02\x02\x01\x00"),
        (0x2085, "\x02\x02\x20\x85"),
        (0x208511, "\x02\x03\x20\x85\x11"),
        (-128, "\x02\x01\x80"),
        (-129, "\x02\x02\xff\x7f"),
    ],
)
def test_encode_int(value, raw):
    encoder = BEREncoder()
    assert encoder.encode_int(value) == raw


@pytest.mark.parametrize(
    "raw, value",
    [
        (float("+inf"), "\t\x01@"),
        (float("-inf"), "\t\x01A"),
        (float("nan"), "\t\x01B"),
        (float("-0"), "\t\x01C"),
        (float("1"), "\t\x080x031E+0"),
        (float("1.5"), "\t\t0x0315E-1"),
    ],
)
def test_encode_real(raw, value):
    encoder = BEREncoder()
    assert encoder.encode_real(raw) == value


@pytest.mark.parametrize("value", ["\x05\x00"])
def test_encode_null(value):
    encoder = BEREncoder()
    assert encoder.encode_null() == value


@pytest.mark.parametrize(
    "oid,raw",
    [
        ("1.3.6.1.2.1.1.5.0", "\x06\x08+\x06\x01\x02\x01\x01\x05\x00"),
        ("1.3.6.0", "\x06\x03+\x06\x00"),
        ("1.3.6.127", "\x06\x03+\x06\x7f"),
        ("1.3.6.128", "\x06\x04+\x06\x81\x00"),
        ("1.3.6.255", "\x06\x04+\x06\x81\x7f"),
        ("1.3.6.256", "\x06\x04+\x06\x82\x00"),
        ("1.3.6.16383", "\x06\x04+\x06\xff\x7f"),
        ("1.3.6.16384", "\x06\x05+\x06\x81\x80\x00"),
        ("1.3.6.65535", "\x06\x05+\x06\x83\xff\x7f"),
        ("1.3.6.65535", "\x06\x05+\x06\x83\xff\x7f"),
        ("1.3.6.2097151", "\x06\x05+\x06\xff\xff\x7f"),
        ("1.3.6.2097152", "\x06\x06+\x06\x81\x80\x80\x00"),
        ("1.3.6.16777215", "\x06\x06+\x06\x87\xff\xff\x7f"),
        ("1.3.6.268435455", "\x06\x06+\x06\xff\xff\xff\x7f"),
        ("1.3.6.268435456", "\x06\x07+\x06\x81\x80\x80\x80\x00"),
        ("1.3.6.2147483647", "\x06\x07+\x06\x87\xff\xff\xff\x7f"),
    ],
)
def test_encode_oid(oid, raw):
    encoder = BEREncoder()
    assert encoder.encode_oid(oid) == raw
