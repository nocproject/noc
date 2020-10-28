# ----------------------------------------------------------------------
# RateLimit
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional
from time import perf_counter_ns


NS = 1_000_000_000.0


class BaseRateLimit(object):
    """
    Limit calls to `wait*` methods to `rate` requests per second.
    """

    def __init__(self, rate: float):
        self.min_delta: int = int(NS / rate)
        self.next: Optional[int] = None

    def get_sleep_timeout(self) -> Optional[float]:
        """
        Get timeout for next sleep
        :return:
        """
        ts = perf_counter_ns()
        if not self.next:
            # First call, not limited
            self.next = ts + self.min_delta
            return None
        delta = self.next - ts
        if delta > 0:
            # Incomplete interval, limited
            self.next += self.min_delta
            return float(delta) / NS
        # Interval passed, not limited
        self.next += delta % self.min_delta
        return None
