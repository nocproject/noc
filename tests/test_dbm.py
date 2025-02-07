# ----------------------------------------------------------------------
# noc.core.convert.dbm unittests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.convert.dbm import dbm2mw, mw2dbm


@pytest.mark.parametrize("config, expected", [(0, 1.0), (10, 10.0)])
def test_dbm2mw(config, expected):
    assert dbm2mw(config) == expected


@pytest.mark.parametrize("config, expected", [(1, 0.0), (10, 10.0), (0.0, 0.0)])
def test_mw2dbm(config, expected):
    assert mw2dbm(config) == expected
