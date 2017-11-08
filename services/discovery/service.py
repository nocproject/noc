#!./bin/python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Discovery
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

import tornado.gen
# Python modules
# Third-party modules
import tornado.ioloop
# NOC modules
from noc.config import config
from noc.core.scheduler.scheduler import Scheduler
from noc.core.service.base import Service


class DiscoveryService(Service):
    name = "discovery"
    leader_group_name = "discovery-%(pool)s"
    pooled = True
    require_nsq_writer = True
    process_name = "noc-%(name).10s-%(pool).5s"

    def __init__(self):
        super(DiscoveryService, self).__init__()
        self.send_callback = None
        self.slot_number = 0
        self.total_slots = 0

    @tornado.gen.coroutine
    def on_activate(self):
        self.slot_number, self.total_slots = yield self.acquire_slot()
        if self.total_slots > 1:
            self.logger.info(
                "Enabling distributed mode: Slot %d/%d",
                self.slot_number, self.total_slots
            )
            ifilter = {
                "key": {
                    "$mod": [
                        self.total_slots,
                        self.slot_number
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
            pool=config.pool,
            reset_running=True,
            max_threads=config.discovery.max_threads,
            ioloop=self.ioloop,
            filter=ifilter,
            service=self,
            sample=config.discovery.sample
        )
        self.scheduler.run()

    def get_mon_data(self):
        r = super(DiscoveryService, self).get_mon_data()
        if self.scheduler:
            self.scheduler.apply_metrics(r)
        return r


if __name__ == "__main__":
    DiscoveryService().start()
