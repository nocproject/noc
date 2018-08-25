# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# noc.core.snmp.ber tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest
# NOC modules
from noc.core.snmp.ber import BEREncoder, BERDecoder


def test_decode_int():
    decoder = BERDecoder()
    assert decoder.parse_int("") == 0
    assert decoder.parse_int("\x00") == 0
    assert decoder.parse_int("\x01") == 1
    assert decoder.parse_int("\x7f") == 127
    assert decoder.parse_int("\x00\x80") == 128
    assert decoder.parse_int("\x01\x00") == 256
    assert decoder.parse_int("\x80") == -128
    assert decoder.parse_int("\xff\x7f")


def test_decode_real():
    decoder = BERDecoder()
    assert decoder.parse_real("@") == float("+inf")
    assert decoder.parse_real("A") == float("-inf")
    # Failed
    # assert decoder.parse_real("B") == float("nan")
    # assert decoder.parse_real("C") == float("-0")
    assert decoder.parse_real("\x031E+0") == float("1")
    assert decoder.parse_real("\x0315E-1") == float("1.5")


@pytest.mark.xfail()
def test_decode_p_bitstring():
    raise NotImplementedError()


def test_decode_p_octetstring():
    decoder = BERDecoder()
    assert decoder.parse_p_octetstring("test") == "test"
    assert decoder.parse_p_octetstring("public") == "public"
    assert decoder.parse_p_octetstring("") == ""


@pytest.mark.xfail()
def test_decode_p_t61_string():
    raise NotImplementedError()


@pytest.mark.xfail()
def test_decode_c_octetstring():
    raise NotImplementedError()


@pytest.mark.xfail()
def test_decode_c_t61_string():
    raise NotImplementedError()


def test_decode_null():
    decoder = BERDecoder()
    assert decoder.parse_null("\x00") is None


@pytest.mark.xfail()
def test_decode_a_ipaddress():
    raise NotImplementedError()


def test_decode_p_oid():
    decoder = BERDecoder()
    assert decoder.parse_p_oid("+\x06\x01\x02\x01\x01\x05\x00") == "1.3.6.1.2.1.1.5.0"


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


@pytest.mark.xfail()
def test_encode_tlv():
    raise NotImplementedError()


def test_encode_octet_string():
    encoder = BEREncoder()
    assert encoder.encode_octet_string("test") == "\x04\x04test"
    assert encoder.encode_octet_string("public") == "\x04\x06public"
    assert encoder.encode_octet_string("") == "\x04\x00"


@pytest.mark.xfail()
def test_encode_sequence():
    raise NotImplementedError()


@pytest.mark.xfail()
def test_encode_choice():
    raise NotImplementedError()


def test_encode_int():
    encoder = BEREncoder()
    assert encoder.encode_int(0) == "\x02\x01\x00"
    assert encoder.encode_int(1) == "\x02\x01\x01"
    assert encoder.encode_int(127) == "\x02\x01\x7f"
    assert encoder.encode_int(128) == "\x02\x02\x00\x80"
    assert encoder.encode_int(256) == "\x02\x02\x01\x00"
    assert encoder.encode_int(-128) == "\x02\x01\x80"
    assert encoder.encode_int(-129) == "\x02\x02\xff\x7f"


def test_encode_real():
    encoder = BEREncoder()
    assert encoder.encode_real(float("+inf")) == "\t\x01@"
    assert encoder.encode_real(float("-inf")) == "\t\x01A"
    assert encoder.encode_real(float("nan")) == "\t\x01B"
    assert encoder.encode_real(float("-0")) == "\t\x01C"
    assert encoder.encode_real(float("1")) == "\t\x080x031E+0"
    assert encoder.encode_real(float("1.5")) == "\t\t0x0315E-1"


def test_encode_null():
    encoder = BEREncoder()
    assert encoder.encode_null() == "\x05\x00"


def test_encode_oid():
    encoder = BEREncoder()
    assert encoder.encode_oid("1.3.6.1.2.1.1.5.0") == "\x06\x08+\x06\x01\x02\x01\x01\x05\x00"
