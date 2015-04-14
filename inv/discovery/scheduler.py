## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-discovery scheduler
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import datetime
import random
## NOC modules
from noc.lib.scheduler.scheduler import Scheduler
from noc.lib.solutions import solutions_roots


class DiscoveryScheduler(Scheduler):
    def __init__(self, daemon=None):
        self.daemon = daemon
        super(DiscoveryScheduler, self).__init__(
            "inv.discovery", initial_submit=daemon is not None,
            reset_running=daemon is not None
        )
        self.register_all(
            os.path.join("inv", "discovery", "jobs"),
            exclude=["base.py"])
        for r in solutions_roots():
            jd = os.path.join(r, "discovery", "jobs")
            if os.path.isdir(jd):
                self.register_all(jd)

    def can_run(self, job):
        if not super(DiscoveryScheduler, self).can_run(job):
            return False
        group = job.get_group()
        if group is not None:
            with self.running_lock:
                return group not in self.running_count
        return True
