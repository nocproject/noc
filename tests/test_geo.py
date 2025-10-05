# ---------------------------------------------------------------------
# Geography/Geometry conversion functions
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.gis.geo import ll_to_xy


@pytest.fixture(params=list(range(1, 19)))
def zoom_level(request):
    return request.param


def test_zero_point(zoom_level):
    C = ll_to_xy(zoom_level, (0, 0))
    assert (2 ** (zoom_level - 1), 2 ** (zoom_level - 1)) == C
