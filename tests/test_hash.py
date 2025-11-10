# ----------------------------------------------------------------------
# Test noc.core.hash functions
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.hash import hash_str, hash_int, dict_hash_int, dict_hash_int_args


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0, b"J^\xa04\xb0\x0b\xaf\xb6"),
        ("0", b"J^\xa04\xb0\x0b\xaf\xb6"),
        (None, b"\x1a3\x12\x943.\xcdm"),
        ("None", b"\x1a3\x12\x943.\xcdm"),
    ],
)
def test_hash_str(value, expected):
    assert hash_str(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0, 5358896754769768374),
        ("0", 5358896754769768374),
        (None, 1887873096521534829),
        ("None", 1887873096521534829),
    ],
)
def test_hash_int(value, expected):
    assert hash_int(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ({}, -2954230017111125474),
        ({"k": 1}, -7829327169641555127),
        ({"k": "1"}, -7829327169641555127),
        ({"k": 1, "v": "2"}, 6473659485526827658),
        ({"k": 1, "v": None}, 1975760527053142894),
        ({"k": 1, "v": "None"}, 1975760527053142894),
    ],
)
def test_dict_hash_int(value, expected):
    assert dict_hash_int(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ({}, -2954230017111125474),
        ({"k": 1}, -7829327169641555127),
        ({"k": "1"}, -7829327169641555127),
        ({"k": 1, "v": "2"}, 6473659485526827658),
        ({"k": 1, "v": None}, 1975760527053142894),
        ({"k": 1, "v": "None"}, 1975760527053142894),
    ],
)
def test_dict_hash_int_args(value, expected):
    assert dict_hash_int_args(**value) == expected
