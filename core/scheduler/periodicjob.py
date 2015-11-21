# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Periodic Job Class
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import time
import datetime
## NOC modules
from job import Job


class PeriodicJob(Job):
    # Repeat interval in seconds
    interval = 1
    # Interval after failure (S_FAIL)
    failed_interval = 1
    # Shift start time to random offset
    use_offset = False

    def get_interval(self):
        """
        Returns next repeat interval
        """
        return self.interval

    def get_failed_interval(self):
        return self.failed_interval

    def schedule_next(self, status):
        interval = None
        if status in (self.E_SUCCESS, self.E_EXCEPTION):
            interval = self.get_interval()
        elif status in (self.E_FAILED, self.E_DEFERRED):
            interval = self.get_failed_interval()
        if interval:
            now = time.mktime(datetime.datetime.now().timetuple())
            # Select base time
            if self.use_offset:
                t0 = now // interval * interval
                t0 -= interval * self.attrs[self.ATTR_OFFSET]
            else:
                t0 = time.mktime(self.attrs[self.ATTR_TS].timetuple())
            # Skip all fully passed intervals
            t0 += (now - t0) // interval * interval
            if t0 < now:
                # To next interval
                t0 += interval
            ts = datetime.datetime.fromtimestamp(t0)
            self.scheduler.set_next_run(
                self.attrs[self.ATTR_CLASS],
                self.attrs[self.ATTR_KEY],
                status=status,
                ts=ts,
                duration=self.duration
            )
        else:
            # Remove broken job
            self.remove_job()
