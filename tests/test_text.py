# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# noc.lib.text tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Thirt-party modules
import pytest
# NOC modules
from noc.lib.text import parse_table


@pytest.mark.parametrize("value,kwargs,expected", [
    (
        "First Second Third\n"
        "----- ------ -----\n"
        "a     b       c\n"
        "ddd   eee     fff\n",
        {},
        [["a", "b", "c"], ["ddd", "eee", "fff"]]
    ),
    (
        "First Second Third\n"
        "----- ------ -----\n"
        "a             c\n"
        "ddd   eee     fff\n",
        {},
        [["a", "", "c"], ["ddd", "eee", "fff"]]
    ),
    (
        "VLAN Status  Name                             Ports\n"
        "---- ------- -------------------------------- ---------------------------------\n"
        "4090 Static  VLAN4090                         f0/5, f0/6, f0/7, f0/8, g0/9\n"
        "                                              g0/10\n",
        {"allow_wrap": True, "n_row_delim": ", "},
        [["4090", "Static", "VLAN4090", "f0/5, f0/6, f0/7, f0/8, g0/9, g0/10"]]
    ),
    (
        " MSTI ID     Vid list\n"
        " -------     -------------------------------------------------------------\n"
        "    CIST     1-11,15-122,124-250,253,257-300,302-445,447-709\n"
        "             ,720-759,770-879,901-3859,3861-4094\n"
        "       1     12-14,123,251-252,254-256,301,446,710-719,760-769,\n"
        "             880-900,3860\n",
        {"allow_wrap": True, "n_row_delim": ","},
        [
            ["CIST", "1-11,15-122,124-250,253,257-300,302-445,447-709,720-759,770-879,901-3859,3861-4094"],
            ["1", "12-14,123,251-252,254-256,301,446,710-719,760-769,880-900,3860"]
        ]
    )
])
def test_parse_table(value, kwargs, expected):
    assert parse_table(value, **kwargs) == expected
