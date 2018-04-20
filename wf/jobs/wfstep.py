# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## WFStep job
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## NOC modules
from noc.lib.scheduler.job import Job
from noc.wf.models.process import Process


class WFStepJob(Job):
    name = "wf.wfstep"
    threaded = True
    ignored = False
    model = Process

    def handler(self, *args, **kwargs):
        self.object.step()
        return True

    def get_schedule(self, status):
        if self.object.sleep_time:
            # Reschedule
            st = self.object.sleep_time
            self.object.sleep_time = None
            self.object.save()
            return (datetime.datetime.now() +
                    datetime.timedelta(seconds=st))
        else:
            # Destroy process and context
            self.object.delete()
            # Remove from schedule
            return None