# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alarm disposition job
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.scheduler.job import Job
from noc.fm.models import ActiveEvent


class AlarmDispositionJob(Job):
    name = "dispose"
    model = ActiveEvent

    def handler(self):
        self.scheduler.correlator.dispose_event(self.object)
        self.scheduler.correlator.update_stats(success=True)
        return True

    def on_exception(self):
        self.scheduler.correlator.mark_as_failed(self.object)
        self.scheduler.correlator.update_stats(success=False)
