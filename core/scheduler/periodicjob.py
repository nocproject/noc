# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Periodic Job Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .job import Job


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
        if status in (self.E_SUCCESS, self.E_EXCEPTION):
            interval = self.get_interval()
        elif status in (self.E_FAILED, self.E_DEFERRED):
            interval = self.get_failed_interval()
        else:
            # Remove broken job
            self.remove_job()
            return
        # Schedule next run
        ts = self.get_next_timestamp(interval,
                                     self.attrs[self.ATTR_OFFSET])
        # Store context
        if self.context_version:
            ctx = self.context or None
            ctx_key = self.get_context_cache_key()
        else:
            ctx = None
            ctx_key = None
        self.scheduler.set_next_run(
            self.attrs[self.ATTR_ID],
            status=status,
            ts=ts,
            duration=self.duration,
            context_version=self.context_version,
            context=ctx,
            context_key=ctx_key
        )
