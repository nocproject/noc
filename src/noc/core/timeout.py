# ----------------------------------------------------------------------
# Timeout primitives
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from asyncio import sleep
from random import random

# NOC modules
from noc.core.perf import metrics

PHI = 1.618033988749895
METRIC_COUNT = "retry_count"
METRIC_TIME = "retry_time_ns"
NS = 1_000_000_000.0


async def retry_timeout(timeout: float = 1.0, name: str | None = None) -> None:
    """
    Randomized retry timeout.

    Await function to get randomized retry interval.

    Args:
        timeout: Mean timeout in seconds.
        name: Optional metric name.
    """

    dt = timeout - timeout / PHI
    t = timeout - dt + random() * 2.0 * dt
    await sleep(t)
    if name:
        metrics[METRIC_COUNT, name] += 1
        metrics[METRIC_TIME, name] += int(t * NS)
