# ----------------------------------------------------------------------
# noc.core.mac unittests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.mac import MAC


def test_mac_mac() -> None:
    x = MAC("00:11:22:33:44:55")
    y = MAC(x)
    assert x is y


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("12:34:56:78:9a:bc", "12:34:56:78:9A:BC"), ("12:34:56:78:9A:BC", "12:34:56:78:9A:BC")],
)
def test_mac_colon(raw: str, expected: str) -> None:
    assert MAC(raw) == expected


@pytest.mark.parametrize(("raw", "expected"), [("0:13:46:50:87:5", "00:13:46:50:87:05")])
def test_mac_colon_short(raw: str, expected: str) -> None:
    assert MAC(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("aabbccddeeff", "AA:BB:CC:DD:EE:FF"), ("AABBCCDDEEFF", "AA:BB:CC:DD:EE:FF")],
)
def test_mac_nosep(raw: str, expected: str) -> None:
    assert MAC(raw) == expected


@pytest.mark.parametrize(("raw", "expected"), [(0xAABBCCDDEEFF, "AA:BB:CC:DD:EE:FF")])
def test_mac_int(raw: int, expected: str) -> None:
    assert MAC(raw) == expected


@pytest.mark.parametrize(("raw", "expected"), [("\xaa\xbb\xcc\xdd\xee\xff", "AA:BB:CC:DD:EE:FF")])
def test_mac_bin(raw: str, expected: str) -> None:
    assert MAC(raw) == expected


@pytest.mark.parametrize(("raw", "expected"), [(b"\xe0\xd9\xe3:\x07\xc0", "E0:D9:E3:3A:07:C0")])
def test_mac_str_bin(raw: bytes, expected: str) -> None:
    assert MAC(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("1234.5678.9ABC", "12:34:56:78:9A:BC"),
        ("1234.5678.9abc", "12:34:56:78:9A:BC"),
        ("0112.3456.789a.bc", "12:34:56:78:9A:BC"),
    ],
)
def test_mac_cisco(raw: str, expected: str) -> None:
    assert MAC(raw) == expected


@pytest.mark.parametrize("raw", ["1234.5678.9abc.def0"])
def test_mac_cisco_error(raw: str) -> None:
    with pytest.raises(ValueError):
        MAC(raw)


@pytest.mark.parametrize(("raw", "expected"), [("123456-789abc", "12:34:56:78:9A:BC")])
def test_mac_dash1(raw: str, expected: str) -> None:
    assert MAC(raw) == expected


@pytest.mark.parametrize(("raw", "expected"), [("aabb-ccdd-eeff", "AA:BB:CC:DD:EE:FF")])
def test_mac_dash3(raw: str, expected: str) -> None:
    assert MAC(raw) == expected


@pytest.mark.parametrize(("raw", "expected"), [("12-34-56-78-9A-BC", "12:34:56:78:9A:BC")])
def test_mac_dash5(raw: str, expected: str) -> None:
    assert MAC(raw) == expected


@pytest.mark.parametrize("raw", ["12-34-56-78-9A-BC-DE", "AB-CD-EF-GH-HJ-KL"])
def test_mac_dash5_error(raw: str) -> None:
    with pytest.raises(ValueError):
        MAC(raw)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (
            MAC("AABBCCDDEEFF") + " -- " + MAC("0011.2233.4455"),
            "AA:BB:CC:DD:EE:FF -- 00:11:22:33:44:55",
        )
    ],
)
def test_mac_str_op(raw, expected) -> None:
    assert raw == expected


@pytest.mark.parametrize(("raw", "expected"), [("AA:BB:CC:DD:EE:FF", "aabb.ccdd.eeff")])
def test_mac_to_cisco(raw: str, expected: str) -> None:
    assert MAC(raw).to_cisco() == expected


@pytest.mark.parametrize(
    ("raw", "config", "expected"),
    [
        ("AA:BB:CC:DD:EE:FF", 0, "AA:BB:CC:DD:EE:FF"),
        ("AA:BB:CC:DD:EE:FF", 1, "AA:BB:CC:DD:EF:00"),
        ("AA:BB:CC:DD:EE:FF", 256, "AA:BB:CC:DD:EF:FF"),
        ("AA:BB:CC:DD:EE:FF", 257, "AA:BB:CC:DD:F0:00"),
        ("AA:BB:CC:DD:EE:FF", 4096, "AA:BB:CC:DD:FE:FF"),
    ],
)
def test_mac_shift(raw: str, config: int, expected: str) -> None:
    assert MAC(raw).shift(config) == expected


@pytest.mark.parametrize(("raw", "expected"), [("AA:BB:CC:DD:EE:FF", 17)])
def test_len(raw: str, expected: int) -> None:
    assert len(MAC(raw)) == expected


@pytest.mark.parametrize(("raw", "expected"), [("AA:BB:CC:DD:EE:FF", 0xAABBCCDDEEFF)])
def test_int(raw: str, expected: int) -> None:
    assert int(MAC(raw)) == expected


@pytest.mark.parametrize(
    "value",
    [
        # VRRP virtual
        "00:00:5E:00:01:01",
        "00:00:5E:00:01:02",
        # Plain MAC
        "AC:DE:48:00:01:02",
        "78:4F:43:01:02:53",
    ],
)
def test_unicast(value: str) -> None:
    assert MAC(value).is_multicast is False


@pytest.mark.parametrize(
    "value",
    [
        # CDP
        "01:00:0C:CC:CC:CC",
        # LLDP
        "01:80:C2:00:00:00",
        "01:80:C2:00:00:03",
        "01:80:C2:00:00:0E",
    ],
)
def test_multicast(value: str) -> None:
    assert MAC(value).is_multicast is True


@pytest.mark.parametrize(
    "value",
    [
        "02:00:0C:CC:CC:CC",
        "36:80:C2:00:00:00",
        "0A:80:C2:00:00:03",
        "1E:80:C2:00:00:0E",
    ],
)
def test_locally_administered(value: str) -> None:
    assert MAC(value).is_locally_administered is True


@pytest.mark.parametrize(
    ("value", "expected"),
    [("AA:BB:CC:DD:EE:FF", 0xAABBCC), ("0:1:2:4:5:6", 0x0102), ("dead.beef.abcd", 0xDEADBE)],
)
def test_oui(value: str, expected: int) -> None:
    assert MAC(value).oui == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (("01:02:03:04:05:06",), True),
        (("01:02:03:04:05:06", "01:02:03:04:05:0a"), True),
        (("01:02:03:04:05:06", "01:02:03:04:05:0a", "01:03:03:04:05:0a"), False),
    ],
)
def test_is_same_oui(value: tuple[str, ...], expected: bool) -> None:
    assert MAC.is_same_oui(value[0], *tuple(value[1:])) is expected


@pytest.mark.parametrize(
    ("s", "e", "dist"),
    [
        ("01:02:03:04:05:06", "01:02:03:04:05:06", 0),
        ("01:02:03:04:05:06", "01:02:03:04:05:07", 1),
        ("01:02:03:04:05:07", "01:02:03:04:05:06", 1),
        ("01:02:03:04:05:06", "01:02:03:04:06:07", 257),
        ("01:02:03:04:06:07", "01:02:03:04:05:06", 257),
    ],
)
def test_distance(s: str, e: str, dist: int) -> None:
    assert MAC.distance(s, e) == dist
