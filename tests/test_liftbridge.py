# ----------------------------------------------------------------------
# Liftbridge client tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.liftbridge.base import LiftBridgeClient


@pytest.mark.parametrize(
    "input,expected", [("test", "__offset.test"), ("test-offset", "__offset.test-offset")]
)
def test_offset_stream(input: str, expected: str):
    client = LiftBridgeClient()
    assert client.get_offset_stream(input) == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        (0, b"\x00\x00\x00\x00\x00\x00\x00\x00"),
        (1, b"\x00\x00\x00\x00\x00\x00\x00\x01"),
        (128, b"\x00\x00\x00\x00\x00\x00\x00\x80"),
        (255, b"\x00\x00\x00\x00\x00\x00\x00\xFF"),
        (256, b"\x00\x00\x00\x00\x00\x00\x01\x00"),
        (123456789, b"\x00\x00\x00\x00\x07\x5b\xcd\x15"),
    ],
)
def test_offset_encode(input: int, expected: bytes):
    client = LiftBridgeClient()
    assert client.encode_offset(input) == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        (b"\x00\x00\x00\x00\x00\x00\x00\x00", 0),
        (b"\x00\x00\x00\x00\x00\x00\x00\x01", 1),
        (b"\x00\x00\x00\x00\x00\x00\x00\x80", 128),
        (b"\x00\x00\x00\x00\x00\x00\x00\xFF", 255),
        (b"\x00\x00\x00\x00\x00\x00\x01\x00", 256),
        (b"\x00\x00\x00\x00\x07\x5b\xcd\x15", 123456789),
    ],
)
def test_offset_decode(input: bytes, expected: int):
    client = LiftBridgeClient()
    assert client.decode_offset(input) == expected
