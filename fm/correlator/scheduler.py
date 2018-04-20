# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Correlator Scheduler
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## NOC modules
from noc.lib.scheduler.scheduler import Scheduler
from noc.fm.correlator.jobs.dispose import AlarmDispositionJob


class CorrelatorScheduler(Scheduler):
    def __init__(self, correlator=None, cleanup=None):
        super(CorrelatorScheduler, self).__init__(
            "fm.correlator", cleanup=cleanup, preserve_order=True)
        self.correlator = correlator
        if correlator:
            # Called from correlator
            # Register all jobs
            self.register_all(os.path.join("fm", "correlator", "jobs"),
                exclude=["base.py"])
            self.reset_running = True
        else:
            # Called from classifier,
            # Register only "dispose" job
            self.register_job_class(AlarmDispositionJob)

    def submit_event(self, event):
        self.submit("dispose", key=event.id)
