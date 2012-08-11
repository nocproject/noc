# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Correlator Scheduler
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.scheduler import Scheduler
from noc.fm.alarmdispositionjob import AlarmDispositionJob


class CorrelatorScheduler(Scheduler):
    def __init__(self, correlator=None, cleanup=None):
        super(CorrelatorScheduler, self).__init__(
            "fm.correlator", cleanup=cleanup)
        self.register_job_class(AlarmDispositionJob)
        self.correlator = correlator

    def submit_event(self, event):
        self.submit("dispose", key=event.id)
