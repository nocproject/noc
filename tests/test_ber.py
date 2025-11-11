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


@pytest.mark.parametrize(("raw", "value"), [(b"\x00", False), (b"\x01", True), (b"", False)])
def test_decode_bool(raw, value):
    decoder = BERDecoder()
    assert decoder.parse_boolean(raw) is value


@pytest.mark.parametrize(
    ("raw", "value"),
    [
        (b"", 0),
        (b"\x00", 0),
        (b"\x01", 1),
        (b"\x7f", 127),
        (b"\x00\x80", 128),
        (b"\x01\x00", 256),
        (b"\x80", -128),
        (b"\xff\x7f", -129),
        (b"\xff\x00\x01", -65535),
        (b"\x20\x85", 0x2085),
        (b"\x20\x85\x11", 0x208511),
    ],
)
def test_decode_int(raw, value):
    decoder = BERDecoder()
    assert decoder.parse_int(raw) == value


@pytest.mark.parametrize(
    ("raw", "value"),
    [
        (b"@", float("+inf")),
        (b"A", float("-inf")),
        (b"\x031E+0", float("1")),
        (b"\x0315E-1", float("1.5")),
        (b"", 0.0),
    ],
)
def test_decode_real(raw, value):
    decoder = BERDecoder()
    assert decoder.parse_real(raw) == value


@pytest.mark.parametrize(("raw", "value"), [(b"B", float("nan")), (b"C", float("-0"))])
def test_decode_real_error(raw, value):
    decoder = BERDecoder()
    with pytest.raises(Exception):
        assert decoder.parse_real(raw) == value


@pytest.mark.parametrize(("raw", "value"), [(b"\x00\xff\x84", b"000000001111111110000100")])
def test_decode_p_bitstring(raw, value):
    decoder = BERDecoder()
    assert decoder.parse_p_bitstring(raw) == value


@pytest.mark.parametrize(("raw", "value"), [(b"test", b"test"), (b"public", b"public"), (b"", b"")])
def test_decode_p_octetstring(raw, value):
    decoder = BERDecoder()
    assert decoder.parse_p_octetstring(raw) == value


@pytest.mark.xfail
def test_decode_p_t61_string():
    raise NotImplementedError()


@pytest.mark.xfail
def test_decode_c_octetstring():
    raise NotImplementedError()


@pytest.mark.xfail
def test_decode_c_t61_string():
    raise NotImplementedError()


@pytest.mark.parametrize("raw", [b"\x00"])
def test_decode_null(raw):
    decoder = BERDecoder()
    assert decoder.parse_null(raw) is None


@pytest.mark.parametrize(("raw", "value"), [(b"\xc0\xa8\x00\x01", "192.168.0.1")])
def test_decode_a_ipaddress(raw, value):
    decoder = BERDecoder()
    assert decoder.parse_a_ipaddress(raw) == value


@pytest.mark.parametrize(
    ("raw", "value"), [(b"+\x06\x01\x02\x01\x01\x05\x00", "1.3.6.1.2.1.1.5.0")]
)
def test_decode_p_oid(raw, value):
    decoder = BERDecoder()
    assert decoder.parse_p_oid(raw) == value


@pytest.mark.xfail
def test_decode_compressed_oid():
    raise NotImplementedError()


@pytest.mark.xfail
def test_decode_sequence():
    raise NotImplementedError()


@pytest.mark.xfail
def test_decode_implicit():
    raise NotImplementedError()


@pytest.mark.xfail
def test_decode_set():
    raise NotImplementedError()


@pytest.mark.xfail
def test_decode_utctime():
    raise NotImplementedError()


@pytest.mark.parametrize(
    ("raw", "value"),
    [
        (b"\x9f\x78\x04\x42\xf6\x00\x00", 123.0),
        # Opaque
        (b"\x44\x07\x9f\x78\x04\x42\xf6\x00\x00", 123.0),
    ],
)
def test_decode_float(raw, value):
    decoder = BERDecoder()
    assert decoder.parse_tlv(raw)[0] == value


@pytest.mark.parametrize(
    ("raw", "value"),
    [
        (b"\x9f\x79\x08\x40\x5e\xc0\x00\x00\x00\x00\x00", 123.0),
        # Opaque
        (b"\x44\x0b\x9f\x79\x08\x40\x5e\xc0\x00\x00\x00\x00\x00", 123.0),
    ],
)
def test_decode_double(raw, value):
    decoder = BERDecoder()
    assert decoder.parse_tlv(raw)[0] == value


@pytest.mark.parametrize(("raw", "value"), [(b"\x44\x81\x06\x04\x04test", b"test")])
def test_decode_opaque(raw, value):
    decoder = BERDecoder()
    assert decoder.parse_tlv(raw)[0] == value


@pytest.mark.parametrize(
    ("tag", "primitive", "data", "value"), [(0x4, True, b"test", b"\x04\x04test")]
)
def test_encode_tlv(tag, primitive, data, value):
    encoder = BEREncoder()
    assert encoder.encode_tlv(tag, primitive, data) == value


@pytest.mark.parametrize(
    ("raw", "value"),
    [(b"test", b"\x04\x04test"), (b"public", b"\x04\x06public"), (b"", b"\x04\x00")],
)
def test_encode_octet_string(raw, value):
    encoder = BEREncoder()
    assert encoder.encode_octet_string(raw) == value


@pytest.mark.parametrize(
    ("value", "raw"),
    [
        (0, b"\x02\x01\x00"),
        (1, b"\x02\x01\x01"),
        (127, b"\x02\x01\x7f"),
        (128, b"\x02\x02\x00\x80"),
        (256, b"\x02\x02\x01\x00"),
        (0x2085, b"\x02\x02\x20\x85"),
        (0x208511, b"\x02\x03\x20\x85\x11"),
        (-128, b"\x02\x01\x80"),
        (-129, b"\x02\x02\xff\x7f"),
    ],
)
def test_encode_int(value, raw):
    encoder = BEREncoder()
    assert encoder.encode_int(value) == raw


@pytest.mark.parametrize(
    ("raw", "value"),
    [
        (float("+inf"), b"\t\x01@"),
        (float("-inf"), b"\t\x01A"),
        (float("nan"), b"\t\x01B"),
        (float("-0"), b"\t\x01C"),
        (float("1"), b"\t\x080x031E+0"),
        (float("1.5"), b"\t\t0x0315E-1"),
    ],
)
def test_encode_real(raw, value):
    encoder = BEREncoder()
    assert encoder.encode_real(raw) == value


@pytest.mark.parametrize("value", [b"\x05\x00"])
def test_encode_null(value):
    encoder = BEREncoder()
    assert encoder.encode_null() == value


@pytest.mark.parametrize(
    ("oid", "raw"),
    [
        ("1.3.6.1.2.1.1.5.0", b"\x06\x08+\x06\x01\x02\x01\x01\x05\x00"),
        ("1.3.6.0", b"\x06\x03+\x06\x00"),
        ("1.3.6.127", b"\x06\x03+\x06\x7f"),
        ("1.3.6.128", b"\x06\x04+\x06\x81\x00"),
        ("1.3.6.255", b"\x06\x04+\x06\x81\x7f"),
        ("1.3.6.256", b"\x06\x04+\x06\x82\x00"),
        ("1.3.6.16383", b"\x06\x04+\x06\xff\x7f"),
        ("1.3.6.16384", b"\x06\x05+\x06\x81\x80\x00"),
        ("1.3.6.65535", b"\x06\x05+\x06\x83\xff\x7f"),
        ("1.3.6.65535", b"\x06\x05+\x06\x83\xff\x7f"),
        ("1.3.6.2097151", b"\x06\x05+\x06\xff\xff\x7f"),
        ("1.3.6.2097152", b"\x06\x06+\x06\x81\x80\x80\x00"),
        ("1.3.6.16777215", b"\x06\x06+\x06\x87\xff\xff\x7f"),
        ("1.3.6.268435455", b"\x06\x06+\x06\xff\xff\xff\x7f"),
        ("1.3.6.268435456", b"\x06\x07+\x06\x81\x80\x80\x80\x00"),
        ("1.3.6.2147483647", b"\x06\x07+\x06\x87\xff\xff\xff\x7f"),
        ("1.3.6.4160759936", b"\x06\x07+\x06\x8f\xc0\x80\xd1\x00"),
    ],
)
def test_encode_oid(oid, raw):
    encoder = BEREncoder()
    assert encoder.encode_oid(oid) == raw


@pytest.mark.parametrize(
    ("data", "result"),
    [
        (b"\x02\x04w\x05\xd3\xc9", b"0\x06\x02\x04w\x05\xd3\xc9"),
        (
            [
                b"\x02\x04w\x05\xd3\xc9",
                b"\x02\x01\x00",
                b"\x02\x01\x00",
                b"0\x0e0\x0c\x06\x08+\x06\x01\x02\x01\x01\x06\x00\x05\x00",
            ],
            b"0\x1c\x02\x04w\x05\xd3\xc9\x02\x01\x00\x02\x01\x000\x0e0\x0c\x06\x08"
            b"+\x06\x01\x02\x01\x01\x06\x00\x05\x00",
        ),
    ],
)
def test_encode_sequence(data, result):
    encoder = BEREncoder()
    assert encoder.encode_sequence(data) == result


@pytest.mark.parametrize(
    ("tag", "data", "result"),
    [
        (0, b"\x02\x04w\x05\xd3\xc9", b"\xa0\x06\x02\x04w\x05\xd3\xc9"),
        (
            0,
            [
                b"\x02\x04w\x05\xd3\xc9",
                b"\x02\x01\x00",
                b"\x02\x01\x00",
                b"0\x0e0\x0c\x06\x08+\x06\x01\x02\x01\x01\x06\x00\x05\x00",
            ],
            (
                b"\xa0\x1c\x02\x04w\x05\xd3\xc9\x02\x01\x00\x02\x01\x000\x0e0\x0c\x06\x08"
                b"+\x06\x01\x02\x01\x01\x06\x00\x05\x00"
            ),
        ),
    ],
)
def test_encode_choice(tag, data, result):
    encoder = BEREncoder()
    assert encoder.encode_choice(tag, data) == result
