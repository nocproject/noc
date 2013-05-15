# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Scheduler Auto-submitable Interval Job Class
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from intervaljob import IntervalJob


class AutoIntervalJob(IntervalJob):
    interval = 86400
    randomize = False
    initial_submit_interval = 86400

    @classmethod
    def initial_submit(cls, scheduler, keys):
        if not keys:
            cls.submit(
                scheduler,
                interval=cls.interval,
                randomize=cls.randomize
            )
