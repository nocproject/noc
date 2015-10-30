#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Scheduler
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Third-party modules
import tornado.ioloop
import tornado.gen
## NOC modules
from noc.core.service.base import Service
from noc.core.scheduler.scheduler import Scheduler


class SchedulerService(Service):
    name = "scheduler"
    leader_group_name = "scheduler"

    def __init__(self):
        super(SchedulerService, self).__init__()
        self.scheduler = None

    @tornado.gen.coroutine
    def on_activate(self):
        self.scheduler = Scheduler(
            "discovery",
            reset_running=True,
            ioloop=self.ioloop
        )
        self.scheduler.run()

if __name__ == "__main__":
    SchedulerService().start()
