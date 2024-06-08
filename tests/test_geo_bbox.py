# ----------------------------------------------------------------------
# noc.core.geo.bbox tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest
from geojson import Polygon

# NOC modules
from noc.core.geo import get_bbox


@pytest.mark.parametrize(
    "input,expected",
    [
        ([0, 10, 0, 20], [[[0, 0], [10, 0], [10, 20], [0, 20], [0, 0]]]),
        ([10, 0, 0, 20], [[[0, 0], [10, 0], [10, 20], [0, 20], [0, 0]]]),
        ([0, 10, 20, 0], [[[0, 0], [10, 0], [10, 20], [0, 20], [0, 0]]]),
        ([-200, 10, 0, 20], [[[-180, 0], [10, 0], [10, 20], [-180, 20], [-180, 0]]]),
        ([0, 200, 0, 20], [[[0, 0], [180, 0], [180, 20], [0, 20], [0, 0]]]),
        ([0, 10, 0, 100], [[[0, 0], [10, 0], [10, 90], [0, 90], [0, 0]]]),
        ([0, 10, 0, -100], [[[0, -90], [10, -90], [10, 0], [0, 00], [0, -90]]]),
    ],
)
def test_get_bbox(input, expected):
    bbox = get_bbox(*input)
    assert isinstance(bbox, Polygon)
    assert bbox.type == "Polygon"
    assert bbox.coordinates == expected
    with pytest.raises(ValueError):
        get_bbox(0, 0, 0, 0)
