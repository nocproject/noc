# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Correlator Scheduler
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import inspect
## NOC modules
from noc.lib.scheduler.scheduler import Scheduler
from noc.lib.scheduler.job import Job
from noc.fm.correlator.jobs.dispose import AlarmDispositionJob


class CorrelatorScheduler(Scheduler):
    def __init__(self, correlator=None, cleanup=None):
        super(CorrelatorScheduler, self).__init__(
            "fm.correlator", cleanup=cleanup)
        self.correlator = correlator
        if correlator:
            # Auto-register jobs
            prefix = os.path.join("fm", "correlator", "jobs")
            for f in os.listdir(prefix):
                if (f in ("__init__.py", "base.py") or
                    not f.endswith(".py")):
                    continue
                m_name = "noc.fm.correlator.jobs.%s" % f[:-3]
                m = __import__(m_name, {}, {}, "*")
                for on in dir(m):
                    o = getattr(m, on)
                    if (inspect.isclass(o) and issubclass(o, Job) and
                        o.__module__.startswith(m_name)):
                        self.register_job_class(o)
        else:
            # Called from classifier,
            # Register only "dispose" job
            self.register_job_class(AlarmDispositionJob)

    def submit_event(self, event):
        self.submit("dispose", key=event.id)
