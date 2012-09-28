# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Job scheduler
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## NOC modules
from noc.lib.scheduler.scheduler import Scheduler
from noc.settings import INSTALLED_APPS


class JobScheduler(Scheduler):
    def __init__(self, daemon=None):
        self.daemon = daemon
        super(JobScheduler, self).__init__(
            "main.jobs",
            initial_submit=daemon is not None,
            reset_running=daemon is not None
        )
        # Install application jobs
        for app in INSTALLED_APPS:
            if not app.startswith("noc."):
                continue
            p = app.split(".")[1:] + ["jobs"]
            pp = os.path.join(*p)
            if os.path.isdir(pp):
                self.register_all(pp)
