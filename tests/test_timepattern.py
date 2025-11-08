# ----------------------------------------------------------------------
# noc.core.timepattern unittests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime

# Third-party modules
import pytest

# NOC modules
from noc.core.timepattern import TimePattern, TimePatternList


@pytest.mark.parametrize(
    ("config", "year", "month", "day", "expected"),
    [
        ("13", 2005, 3, 13, True),
        ("02", 2005, 3, 13, False),
        ("01-15", 2005, 3, 13, True),
        ("01.03", 2005, 3, 13, False),
        ("13.03", 2005, 3, 13, True),
        ("01.03-02.04", 2005, 3, 13, True),
        ("13.03.2005", 2005, 3, 13, True),
        ("01.03.2005-15.03.2005", 2005, 3, 13, True),
        ("sun", 2005, 3, 13, True),
        ("fri", 2005, 3, 13, False),
        ("fri-sun", 2005, 3, 13, True),
        (None, 2005, 3, 13, True),
    ],
)
def test_timepattern(config, year, month, day, expected):
    assert TimePattern(config).match(datetime.datetime(year=year, month=month, day=day)) == expected


@pytest.mark.parametrize("config", ["zho"])
def test_timepattern_error(config):
    with pytest.raises(Exception):
        assert TimePattern(config)


@pytest.mark.parametrize(
    ("config", "year", "month", "day", "expected"),
    [
        (["13", "01-15"], 2005, 3, 13, True),
        (["13.03.2005", "01-15"], 2005, 3, 13, True),
        (["fri", "01.03"], 2005, 3, 13, False),
    ],
)
def test_timepattern_list(config, year, month, day, expected):
    tp = TimePatternList(config)
    for i in tp.patterns:
        assert TimePattern(i).match(datetime.datetime(year=year, month=month, day=day)) == expected
