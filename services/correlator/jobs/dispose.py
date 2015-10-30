# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alarm disposition job
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.scheduler.job import Job
from noc.fm.models import ActiveEvent


class DisposeJob(Job):
    name = "dispose"
    model = ActiveEvent

    def handler(self):
        self.scheduler.correlator.dispose_event(self.object)
