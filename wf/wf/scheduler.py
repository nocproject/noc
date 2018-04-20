# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## WF Job scheduler
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
from collections import defaultdict
## NOC modules
from noc.lib.scheduler.scheduler import Scheduler


class WFScheduler(Scheduler):
    def __init__(self, daemon=None):
        self.daemon = daemon
        super(WFScheduler, self).__init__(
            "wf.jobs",
            initial_submit=daemon is not None,
            reset_running=daemon is not None
        )
        self.register_all(
            os.path.join("wf", "jobs"),
            exclude=["base.py"])
