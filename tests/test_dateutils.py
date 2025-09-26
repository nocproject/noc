# ----------------------------------------------------------------------
#  Test dateutils
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime

# Third-party modules
import pytest

# NOC modules
from noc.core.dateutils import hits_in_range


def test_hits_in_range():
    start = datetime.datetime(2017, 9, 1)
    stop = datetime.datetime(2017, 9, 2)
    t0 = start - datetime.timedelta(hours=2)
    t1 = start - datetime.timedelta(hours=1)
    t2 = start + datetime.timedelta(hours=1)
    t3 = stop - datetime.timedelta(hours=1)
    t4 = stop + datetime.timedelta(hours=1)
    t5 = stop + datetime.timedelta(hours=2)
    # Empty list leads to 0
    assert hits_in_range([], start, stop) == 0
    # Check start hit
    assert hits_in_range([start], start, stop) == 1
    # Check stop hit
    assert hits_in_range([stop], start, stop) == 1
    # Check pure start & stop hits
    assert hits_in_range([start, stop], start, stop) == 2
    # Check start, stop & intermediate value
    assert hits_in_range([start, t2, stop], start, stop) == 3
    # Check start, stop & 2 intermediate values
    assert hits_in_range([start, t2, t3, stop], start, stop) == 4
    assert hits_in_range([t1, t4], start, stop) == 0
    assert hits_in_range([t1, start, stop, t4], start, stop) == 2
    assert hits_in_range([t0, t1, t2, t3, t4, t5], start, stop) == 2
    assert hits_in_range([t0, t1, start, t2, t3, stop, t4, t5], start, stop) == 4


@pytest.fixture(
    params=[
        # 1s
        (datetime.timedelta(seconds=1), 1.0),
        # 1m
        (datetime.timedelta(minutes=1), 60.0),
        # 1h
        (datetime.timedelta(hours=1), 3600.0),
        # 1day
        (datetime.timedelta(days=1), 86400.0),
        # 7days
        (datetime.timedelta(days=7), 604800.0),
        # 1mks
        (datetime.timedelta(microseconds=1), 1e-6),
        # 1day 1h 1m 1s 1msk
        (datetime.timedelta(days=1, hours=1, minutes=1, microseconds=1), 90060.000001),
    ]
)
def total_seconds_data(request):
    return request.param


def test_total_seconds(total_seconds_data):
    d, s = total_seconds_data
    assert d.total_seconds() == s
