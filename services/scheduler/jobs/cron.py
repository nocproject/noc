# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Cron Job Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from noc.core.scheduler.periodicjob import PeriodicJob
from noc.main.models.crontab import CronTab


class CronJob(PeriodicJob):
    model = CronTab

    def handler(self, **kwargs):
        self.object.run()

    def schedule_next(self, status):
        # Get next run
        ts = self.object.get_next()
        if not ts:
            # Remove disabled job
            self.remove_job()
            return
        self.scheduler.set_next_run(
            self.attrs[self.ATTR_ID],
            status=status,
            ts=ts,
            duration=self.duration
        )
