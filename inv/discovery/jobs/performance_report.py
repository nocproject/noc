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
        ru = resource.getrusage(resource.RUSAGE_SELF)
        logging.info("CPU(U/S): %s/%s MEM(RSS): %s" % (ru.ru_utime, ru.ru_stime, ru.ru_maxrss))
        return True
