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
               failed_interval=60,
               randomize=False, keep_offset=False, ts=None):
        """
        Submit new job to scheduler
        :param cls:
        :param scheduler: Scheduler instance
        :param key: Job key
        :param data: optional dict containting data
        :param interval: In case of success rerun job every *interval*
            seconds
        :param failed_interval: In case of failure rerun job in
            *failed_interval* seconds
        :param randomize: Randomize launch within interval
        :param keep_offset: Keep current time offset from the boundary
            of interval. Overriden by *randomize*
        :param ts: Explicitly set start time
        :return:
        """
        data = data or {}
        if randomize:
            offset = random.random()
        elif keep_offset:
            offset = time.time() % interval / interval
        else:
            offset = 0
        schedule = {
            "interval": interval,
            "offset": offset,
            "randomize": randomize
        }
        if failed_interval:
            schedule["failed_interval"] = failed_interval
        if not ts:
            ts=cls.get_next_aligned(interval, offset=offset)
        scheduler.submit(cls.name, key=key, data=data,
            schedule=schedule, ts=ts)

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
        if status == self.S_SUCCESS:
            offset = self.schedule["offset"]
            return self.get_next_aligned(
                self.schedule["interval"], next=True, offset=offset)
        else:
            fi = self.schedule.get("failed_interval",
                self.schedule.get("interval"))
            if self.schedule.get("randomize"):
                fi *= (0.5 + random.random())
            return (datetime.datetime.now() +
                    datetime.timedelta(seconds=fi))
