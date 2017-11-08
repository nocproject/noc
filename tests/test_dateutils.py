# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
#  Test dateutils
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime

# NOC modules
from noc.lib.dateutils import hits_in_range


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
    #
    assert hits_in_range([t1, t4], start, stop) == 0
    #
    assert hits_in_range([t1, start, stop, t4], start, stop) == 2
    #
    assert hits_in_range([t0, t1, t2, t3, t4, t5], start, stop) == 2
    #
    assert hits_in_range([t0, t1, start, t2, t3, stop, t4, t5], start, stop) == 4
