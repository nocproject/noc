#!./bin/python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Escalator
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import tornado.ioloop
import tornado.gen
# NOC modules
from noc.core.service.base import Service
from noc.core.scheduler.scheduler import Scheduler


class EscalatorService(Service):
    name = "escalator"
    leader_lock_name = "escalator"

    @tornado.gen.coroutine
    def on_activate(self):
        self.scheduler = Scheduler(
            "escalator",
            reset_running=True,
            max_threads=self.config.max_threads,
            ioloop=self.ioloop
        )
        self.scheduler.run()

if __name__ == "__main__":
    EscalatorService().start()
