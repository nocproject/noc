# ---------------------------------------------------------------------
# Test matcher
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.matcher import match


@pytest.mark.parametrize("raw,config,expected", [({}, {}, True), ({"k", "v"}, {}, True)])
def test_zero(raw, config, expected):
    assert match(raw, config) is expected


@pytest.mark.parametrize("raw,config,expected", [({"x": "y"}, {"x": "y"}, True)])
def test_eq(raw, config, expected):
    assert match(raw, config) is expected


@pytest.mark.parametrize(
    "raw,config,expected",
    [
        ({"x": "y", "m": "n"}, {"x": "y", "m": "k"}, False),
        ({"x": "y", "m": "n"}, {"x": "y", "m": "n"}, True),
    ],
)
def test_eq_and(raw, config, expected):
    assert match(raw, config) is expected


@pytest.mark.parametrize(
    "raw,config,expected",
    [
        ({"platform": "S50N", "vendor": "Force10"}, {"platform": {"$regex": "^S"}}, True),
        ({"platform": "E600", "vendor": "Force10"}, {"platform": {"$regex": "^S"}}, False),
        (
            {"platform": "S50N", "vendor": "Force10"},
            {"platform": {"$regex": "^S"}, "vendor": "Force10"},
            True,
        ),
        (
            {"platform": "S50N", "vendor": "Force10"},
            {"platform": {"$regex": "^S"}, "vendor": "Dell"},
            False,
        ),
        (
            {"vendor": "Eltex", "image": "_image.bin"},
            {"image": {"$regex": r"^\S+"}, "vendor": "Eltex"},
            True,
        ),
        ({"vendor": "Eltex"}, {"image": {"$regex": r"^\S+"}, "vendor": "Eltex"}, False),
    ],
)
def test_regex(raw, config, expected):
    assert match(raw, config) is expected


@pytest.mark.parametrize(
    "raw,config,expected",
    [
        ({"platform": "S50N", "vendor": "Force10"}, {"platform": {"$in": ["S50N", "S50P"]}}, True),
        (
            {"platform": "S50N", "vendor": "Force10"},
            {"platform": {"$in": ["S50N", "S50P"]}, "vendor": {"$in": ["Force10", "Dell"]}},
            True,
        ),
        ({"platform": "S25N", "vendor": "Force10"}, {"platform": {"$in": ["S50N", "S50P"]}}, False),
    ],
)
def test_in(raw, config, expected):
    assert match(raw, config) is expected


@pytest.mark.parametrize(
    "raw,config,expected",
    [
        ({"version": "12.2(50)SE"}, {"version": {"$gt": "12.2(48)SE"}}, True),
        ({"version": "12.2(50)SE"}, {"version": {"$gt": "12.2(50)SE"}}, False),
        ({"version": "12.2(50)SE"}, {"version": {"$gt": "12.2(51)SE"}}, False),
    ],
)
def test_gt(raw, config, expected):
    assert match(raw, config) is expected


@pytest.mark.parametrize(
    "raw,config,expected",
    [
        ({"version": "12.2(50)SE"}, {"version": {"$gte": "12.2(48)SE"}}, True),
        ({"version": "12.2(50)SE"}, {"version": {"$gte": "12.2(50)SE"}}, True),
        ({"version": "12.2(50)SE"}, {"version": {"$gte": "12.2(51)SE"}}, False),
    ],
)
def test_gte(raw, config, expected):
    assert match(raw, config) is expected


@pytest.mark.parametrize(
    "raw,config,expected",
    [
        ({"version": "12.2(50)SE"}, {"version": {"$lt": "12.2(48)SE"}}, False),
        ({"version": "12.2(50)SE"}, {"version": {"$lt": "12.2(50)SE"}}, False),
        ({"version": "12.2(50)SE"}, {"version": {"$lt": "12.2(51)SE"}}, True),
    ],
)
def test_lt(raw, config, expected):
    assert match(raw, config) is expected


@pytest.mark.parametrize(
    "raw,config,expected",
    [
        ({"version": "12.2(50)SE"}, {"version": {"$lte": "12.2(48)SE"}}, False),
        ({"version": "12.2(50)SE"}, {"version": {"$lte": "12.2(50)SE"}}, True),
        ({"version": "12.2(50)SE"}, {"version": {"$lte": "12.2(51)SE"}}, True),
    ],
)
def test_lte(raw, config, expected):
    assert match(raw, config) is expected


@pytest.mark.parametrize(
    "raw,config,expected",
    [
        ({"version": "12.2(50)SE"}, {"version": {"$in": ["12.2(48)SE", "12.5(48)SE"]}}, False),
        (
            {"version": "12.2(50)SE"},
            {"version": {"$in": ["12.2(48)SE", "12.5(48)SE", "12.2(50)SE"]}},
            True,
        ),
        (
            {
                "version": "12.2(50)SE",
                "caps": {
                    "DB | Interfaces": 58,
                    "SNMP": True,
                    "SNMP | v1": False,
                    "HP | ProCurve | CLI | Old": True,
                },
            },
            {"caps": {"$in": ["HP | ProCurve | CLI | Old"]}},
            True,
        ),
    ],
)
def test_in2(raw, config, expected):
    assert match(raw, config) is expected


@pytest.mark.parametrize(
    "raw,config,expected",
    [
        ({"labels": ["tag1", "tag2", "tag4"]}, {"labels": {"$all": ["tag1", "tag5"]}}, False),
        ({"labels": ["tag2", "tag4"]}, {"labels": {"$all": ["tag4", "tag2"]}}, True),
    ],
)
def test_all(raw, config, expected):
    assert match(raw, config) is expected


@pytest.mark.parametrize(
    "raw,config,expected",
    [
        (
            {"version": "12.2(33)SE"},
            {"version": {"$gte": "12.2(48)SE", "$lte": "12.2(52)SE"}},
            False,
        ),
        (
            {"version": "12.2(48)SE"},
            {"version": {"$gte": "12.2(48)SE", "$lte": "12.2(52)SE"}},
            True,
        ),
        (
            {"version": "12.2(50)SE"},
            {"version": {"$gte": "12.2(48)SE", "$lte": "12.2(52)SE"}},
            True,
        ),
        (
            {"version": "12.2(52)SE"},
            {"version": {"$gte": "12.2(48)SE", "$lte": "12.2(52)SE"}},
            True,
        ),
        (
            {"version": "12.2(60)SE"},
            {"version": {"$gte": "12.2(48)SE", "$lte": "12.2(52)SE"}},
            False,
        ),
    ],
)
def test_between(raw, config, expected):
    assert match(raw, config) is expected


@pytest.mark.parametrize(
    "raw,config,expected",
    [
        (
            {"version": "12.2(60)SE"},
            {
                "$or": [
                    {"version": {"$gte": "12.3(60)SE"}},
                    {"version": {"$lte": "11.3(60)SE"}},
                ],
            },
            False,
        ),
        (
            {"version": "10.2(60)SE"},
            {
                "$or": [
                    {"version": {"$gte": "12.3(60)SE"}},
                    {"version": {"$lte": "11.3(60)SE"}},
                ],
            },
            True,
        ),
    ],
)
def test_or(raw, config, expected):
    assert match(raw, config) is expected
