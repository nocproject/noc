# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Discovery performance report job
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import resource
from collections import defaultdict
## NOC modules
from noc.lib.scheduler.intervaljob import IntervalJob


class PerformanceReportJob(IntervalJob):
    name = "performance_report"

    def handler(self):
        rc = self.scheduler.get_running_count()
        rr = ", ".join("%s: %s" % (g, rc[g]) for g in rc)
        ru = resource.getrusage(resource.RUSAGE_SELF)
        self.scheduler.info("CPU(U/S): %s/%s MEM(RSS): %s" % (ru.ru_utime, ru.ru_stime, ru.ru_maxrss))
        if rc:
            self.scheduler.info("RUNNING GROUPS: %s" % rr)
        # Thread pool statistics
        sc = defaultdict(int)
        n = 0
        for s in self.scheduler.thread_pool.get_status():
            sc[s["status"]] += 1
            n += 1
        self.scheduler.logger.info(
            "POOL: %d threads (%s)",
            n,
            ", ".join("%s: %s" % (x, sc[x]) for x in sorted(sc))
        )
        #
        return True
