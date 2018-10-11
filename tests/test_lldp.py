# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# noc.core.lldp tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest
# NOC modules
from noc.core.lldp import (lldp_bits_to_caps, lldp_caps_to_bits, LLDP_CAP_OTHER, LLDP_CAP_REPEATER,
                           LLDP_CAP_BRIDGE, LLDP_CAP_WLAN_ACCESS_POINT, LLDP_CAP_ROUTER,
                           LLDP_CAP_TELEPHONE, LLDP_CAP_DOCSIS_CABLE_DEVICE, LLDP_CAP_STATION_ONLY)


@pytest.mark.parametrize(
    "value,expected", [
        # Empty value
        ([], 0),
        # Single bits
        (["other"], 1),
        (["repeater"], 2),
        (["bridge"], 4),
        (["wap"], 8),
        (["router"], 16),
        (["phone"], 32),
        (["docsis"], 64),
        (["station"], 128),
        # Ignore unknown
        (["foobar"], 0),
        (["foo", "bar"], 0),
        # Multi bits
        (["repeater", "bridge"], 6),
        (["other", "repeater", "bridge", "wap", "router", "phone", "docsis", "station"], 255),
        # Case
        (["OtHeR"], 1),
        (["OtHeR", "repeAter"], 3)
    ]
)
def test_lldp_caps_to_bits(value, expected):
    cmap = {
        "other": LLDP_CAP_OTHER,
        "repeater": LLDP_CAP_REPEATER,
        "bridge": LLDP_CAP_BRIDGE,
        "wap": LLDP_CAP_WLAN_ACCESS_POINT,
        "router": LLDP_CAP_ROUTER,
        "phone": LLDP_CAP_TELEPHONE,
        "docsis": LLDP_CAP_DOCSIS_CABLE_DEVICE,
        "station": LLDP_CAP_STATION_ONLY
    }
    assert lldp_caps_to_bits(value, cmap) == expected


@pytest.mark.parametrize(
    "value,expected", [
        # Empty value
        (0, []),
        # Single bit
        (1, ["other"]),
        (2, ["repeater"]),
        (4, ["bridge"]),
        (8, ["wap"]),
        (16, ["router"]),
        (32, ["phone"]),
        (64, ["docsis-cable-device"]),
        (128, ["station-only"]),
        # Multi-bit
        (3, ["other", "repeater"]),
        (255, ["other", "repeater", "bridge", "wap", "router", "phone", "docsis-cable-device", "station-only"])
    ]
)
def test_lldp_bits_to_caps(value, expected):
    assert lldp_bits_to_caps(value) == expected
