# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Periodic Job Class
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import math
## NOC modules
from job import Job


class PeriodicJob(Job):
    # Repeat interval in seconds
    interval = 1
    # Interval after failure (S_FAIL)
    failed_interval = 1
    # Shift start time to random offset
    use_offset = True

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
            interval = self.interval
        elif status in (self.E_FAILED, self.E_DEFERRED):
            interval = self.failed_interval
        if interval:
            now = datetime.datetime.now()
            # Get amount of full intervals passed
            td = (now - self.attrs[self.ATTR_TS])
            so = (td.seconds + td.days * 86400) // interval * interval
            # And add next interval
            so += interval
            # Set next schedule
            delta = datetime.timedelta(seconds=so)
            ts = self.attrs[self.ATTR_TS] + delta
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
