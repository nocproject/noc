# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Scheduler Multi Interval Job Class
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## NOC modules
from intervaljob import IntervalJob
from noc.lib.dateutils import total_seconds


class MultiIntervalJob(IntervalJob):
    """
    MultiIntervalJobs allows to adjust repeat interval
    accoding to amount of time passed from job scheduling time.
    Interval is set as [(T0, I0), ..., (Tn-1, In-1), (None, In)]
    First T0 seconds from scheduling repeat interval will be set to I0,
    Up to T1 seconds from scheduling repeat interval will be set to I1,
    Last repeat interval will be In
    """
    def get_interval(self):
        dt = total_seconds(datetime.datetime.now() - self.scheduler["scheduled"])
        for t, i in self.schedule["interval"]:
            if t is None or t > dt:
                return i
