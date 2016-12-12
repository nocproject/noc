#!/usr/bin/env python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Discovery
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import threading
# Third-party modules
import tornado.ioloop
import tornado.gen
import tornado.httpclient
## NOC modules
from noc.core.service.base import Service
from noc.core.scheduler.scheduler import Scheduler


class DiscoveryService(Service):
    name = "discovery"
    leader_group_name = "discovery-%(pool)s"
    pooled = True
    process_name = "noc-%(name).10s-%(instance).2s-%(pool).3s"
    require_nsq_writer = True

    def __init__(self):
        super(DiscoveryService, self).__init__()
        self.config.use_pg_pool()
        self.scheduler = None
        self.send_callback = None

    @tornado.gen.coroutine
    def on_activate(self):
        #
        # self.setup_pg_connection_pool()
        #
        if self.config.discovery.global_n_instances > 1:
            self.logger.info(
                "Enabling distributed mode: Slot %d of %d, instance %d, offset, %d",
                int(self.config.instance) + int(self.config.discovery.global_offset),
                    int(self.config.discovery.global_n_instances),
                int(self.config.instance),int(self.config.discovery.global_offset)
            )
            ifilter = {
                "key": {
                    "$mod": [
                        int(self.config.discovery.global_n_instances),
                        int(self.config.instance) + int(self.config.discovery.global_offset)
                    ]
                }
            }
        else:
            self.logger.info(
                "Enabling standalone mode"
            )
            ifilter = None
        self.scheduler = Scheduler(
            "discovery",
            pool=self.config.pool,
            reset_running=True,
            max_threads=self.config.discovery.max_threads,
            ioloop=self.ioloop,
            filter=ifilter,
            use_cache=True
        )
        self.scheduler.service = self
        self.scheduler.run()


if __name__ == "__main__":
    DiscoveryService().start()
