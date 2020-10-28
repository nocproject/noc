# ----------------------------------------------------------------------
# noc.core.ratelimit test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from time import perf_counter_ns

# NOC modules
from noc.core.ratelimit.sync import SyncRateLimit

RATE = 10
TRIES = 2 * RATE
NS = 1_000_000_000


def test_sync_rate_limit():
    limit = SyncRateLimit(float(RATE))
    t0 = perf_counter_ns()
    for i in range(TRIES):
        limit.wait()
    delta = perf_counter_ns() - t0
    # TRIES - 1 as the first call should be unlimited
    min_delta = (TRIES - 1) * (NS // RATE)
    assert delta >= min_delta
