#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Discovery
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


class DiscoveryService(Service):
    name = "discovery"
    leader_group_name = "discovery-%(pool)s"
    pooled = True

    def __init__(self):
        super(DiscoveryService, self).__init__()
        self.scheduler = None

    @tornado.gen.coroutine
    def on_activate(self):
        self.scheduler = Scheduler(
            "discovery",
            pool=self.config.pool,
            reset_running=True,
            ioloop=self.ioloop
        )
        self.scheduler.run()

if __name__ == "__main__":
    DiscoveryService().start()
