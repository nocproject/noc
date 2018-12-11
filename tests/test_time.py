# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# noc.core.time tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import time
# NOC modules
from noc.core.backport.time import perf_counter


def test_perf_counter():
    DELTA = 1.0
    t0 = perf_counter()
    time.sleep(DELTA)
    t1 = perf_counter()
    assert t1 - t0 >= DELTA


def test_perf_counter_implementation():
    assert perf_counter != time.time
