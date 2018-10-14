# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# noc.core.script.metrics tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest
# NOC modules
from noc.core.script.metrics import (
    percent, percent_invert, percent_usage, convert_percent_str, sum, subtract, is1, invert0,
    scale
)


@pytest.mark.parametrize(
    "value,total,expected", [
        (10.0, 0, 100.0), (10.0, None, 100.0), (1.0, 10.0, 10.0), (5.0, 10.0, 50.0),
        (9.0, 10.0, 90.0), (10.0, 10.0, 100.0)
    ]
)
def test_percent(value, total, expected):
    assert percent(value, total) == expected


@pytest.mark.parametrize(
    "value,total,expected", [
        (10.0, 0, 100.0), (10.0, None, 100.0), (1.0, 9.0, 10.0), (5.0, 5.0, 50.0),
        (9.0, 0.0, 100.0), (10.0, 10.0, 50.0)
    ]
)
def test_percent_usage(value, total, expected):
    assert percent_usage(value, total) == expected


@pytest.mark.parametrize(
    "value,total,expected", [
        (10.0, 0, 100.0), (10.0, None, 100.0), (1.0, 10.0, 90.0), (5.0, 10.0, 50.0),
        (9.0, 10.0, 10.0), (10.0, 10.0, 0.0)
    ]
)
def test_percent_invert(value, total, expected):
    assert percent_invert(value, total) == expected


@pytest.mark.parametrize(
    "value,expected", [
        ("09%", 9.0), ("09% ", 9.0), ("09", 9.0), ("10%", 10.0), (None, 0)
    ]
)
def test_convert_percent_str(value, expected):
    assert convert_percent_str(value) == expected


@pytest.mark.parametrize(
    "values,expected", [((1.0,), 1.0), ((1.0, 2.0), 3.0), ((1.0, 2.0, 3.0), 6.0)]
)
def test_sum(values, expected):
    assert sum(*values) == expected


@pytest.mark.parametrize(
    "values,expected", [((10.0, 1.0), 9.0), ((10.0, 1.0, 2.0), 7.0), ((10.0, 1.0, 2.0, 3.0), 4.0)]
)
def test_subtract(values, expected):
    assert subtract(*values) == expected


@pytest.mark.parametrize("value,expected", [(0, 0), (1, 1), (2, 0)])
def test_is1(value, expected):
    assert is1(value) == expected


@pytest.mark.parametrize("value,expected", [(-1, 1), (0, 1), (1, 0)])
def test_invert0(value, expected):
    assert invert0(value) == expected


@pytest.mark.parametrize("sf,value,expected", [
    (1, 1, 1),
    (0, 1, 0),
    (10, 5, 50),
    (8, 0.25, 2.0)
])
def test_scale(sf, value, expected):
    f = scale(sf)
    assert f(value) == expected
