# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Discovery performance report job
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import resource
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
        return True
