# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Scheduler Interval Job Class
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import time
import datetime
import random
## NOC modules
from job import Job


class IntervalJob(Job):
    @classmethod
    def submit(cls, scheduler, key=None, data=None, interval=60,
               randomize=False):
        """
        Submit new job to scheduler
        :param cls:
        :param scheduler: Scheduler instance
        :param key: Job key
        :param data: optional dict containting data
        :param interval: In case of success rerun job every *interval*
            seconds
        :param randomize: Randomize launch within interval
        :return:
        """
        data = data or {}
        if randomize:
            offset = random.random()
        else:
            offset = 0
        data[cls.JOB_NS] = {
            "interval": interval,
            "offset": offset
        }
        scheduler.submit(cls.name, key, data,
            cls.get_next_aligned(interval, offset=offset))

    @classmethod
    def get_next_aligned(cls, interval, next=False, offset=0):
        """
        Get next time in future aligned to interval
        :param interval:
        :return:
        """
        t = int(time.time())
        ts = (t // interval) * interval
        if next or ts < t:
            ts += interval
        if offset:
            ts += offset * interval
        return datetime.datetime.fromtimestamp(ts)

    def get_schedule(self, status):
        offset = self.job_data["offset"]
        return self.get_next_aligned(
            self.job_data["interval"], next=True, offset=offset)
