## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-discovery scheduler
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## NOC modules
from noc.lib.scheduler.scheduler import Scheduler


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

    def can_run(self, job):
        group = job.get_group()
        if group is not None:
            with self.running_lock:
                return group not in self.running_count
        return True