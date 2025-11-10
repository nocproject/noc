# ----------------------------------------------------------------------
# noc.core.geo test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest
from geopy.point import Point

# NOC modules
from noc.core.geo import _get_point, distance, bearing, bearing_sym


@pytest.mark.parametrize(
    ("config", "expected"),
    [
        ([55.754854, 37.618645], (37.618645, 55.754854, 0.0)),
        ([64.510929, 40.509504], (40.509504, 64.510929, 0.0)),
        ([160.024824, 55.735127], (55.735127, 160.024824, 0.0)),
    ],
)
def test_geo_point(config, expected):
    assert _get_point(config) == Point(*expected)


@pytest.mark.parametrize(
    ("config", "config1", "expected"),
    [
        ([37.618645, 55.754854], [37.621756, 55.753390], 254),
        ([64.510929, 40.509504], [64.548181, 40.561689], 6598),
        ([160.024824, 55.735127], [161.156416, 55.455182], 77849),
    ],
)
def test_geo_distance(config, config1, expected):
    assert int(distance(config, config1)) == expected


@pytest.mark.parametrize(
    ("config", "config1", "expected"),
    [
        ([55.754854, 37.618645], [55.753390, 37.621756], 339),
        ([64.510929, 40.509504], [64.548181, 40.561689], 28),
        ([160.024824, 55.735127], [161.156416, 55.455182], 113),
    ],
)
def test_geo_bearing(config, config1, expected):
    assert int(bearing(config, config1)) == expected


@pytest.mark.parametrize(
    ("config", "config1", "expected"),
    [
        ([55.754854, 37.618645], [55.753390, 37.621756], "N"),
        ([64.510929, 40.509504], [64.548181, 40.561689], "NE"),
        ([160.024824, 55.735127], [161.156416, 55.455182], "SE"),
    ],
)
def test_geo_bearing_sym(config, config1, expected):
    assert bearing_sym(config, config1) == expected
