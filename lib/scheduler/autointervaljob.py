# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Scheduler Auto-submitable Interval Job Class
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.config import config

# NOC modules
from intervaljob import IntervalJob


class AutoIntervalJob(IntervalJob):
    interval = config.scheduler.autointervaljob_interval
    randomize = False
    initial_submit_interval = config.scheduler.autointervaljob_initial_submit_interval

    @classmethod
    def initial_submit(cls, scheduler, keys):
        if not keys:
            cls.submit(
                scheduler,
                interval=cls.interval,
                randomize=cls.randomize
            )
