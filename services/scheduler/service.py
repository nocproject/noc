#!./bin/python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Scheduler
# ----------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

import tornado.gen
# Third-party modules
import tornado.ioloop
# NOC modules
from noc.config import config
from noc.core.scheduler.scheduler import Scheduler
from noc.core.service.base import Service


class SchedulerService(Service):
    name = "scheduler"
    leader_group_name = "scheduler"
    leader_lock_name = "scheduler"

    @tornado.gen.coroutine
    def on_activate(self):
        self.scheduler = Scheduler(
            "scheduler",
            reset_running=True,
            max_threads=config.scheduler.max_threads,
            ioloop=self.ioloop
        )
        self.scheduler.run()


if __name__ == "__main__":
    SchedulerService().start()
