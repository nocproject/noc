# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Correlator performance report job
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import time
import logging
## NOC modules
from noc.lib.scheduler.intervaljob import IntervalJob


class PerformanceReportJob(IntervalJob):
    name = "performance_report"

    def handler(self):
        c = self.scheduler.correlator
        count = c.stat_count
        success_count = c.stat_success_count
        t = time.time()
        dt = t - c.stat_start
        if dt:
            perf = count / dt
        else:
            perf = 0
        logging.info(
            "%d events has been disposed (success: %d, failed: %d). "
            "%s seconds elapsed. %6.2f events/sec" % (
                count, success_count, count - success_count, dt, perf))
        c.reset_stats()
        return True
