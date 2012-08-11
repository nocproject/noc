# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alarm disposition job class
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.scheduler.job import Job
from noc.fm.models import ActiveEvent


class AlarmDispositionJob(Job):
    name = "dispose"

    def handler(self):
        self.event = ActiveEvent.objects.filter(id=self.key).first()
        if self.event:
            self.scheduler.correlator.dispose_event(self.event)
            self.scheduler.correlator.update_stats(success=True)
        return True

    def on_exception(self):
        if hasattr(self, "event"):
            self.scheduler.correlator.mark_as_failed(self.event)
            self.scheduler.correlator.update_stats(success=False)
