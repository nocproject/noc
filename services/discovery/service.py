#!./bin/python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Discovery
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
# Third-party modules
import tornado.ioloop
import tornado.gen
# NOC modules
from noc.config import config
from noc.core.service.base import Service
from noc.core.scheduler.scheduler import Scheduler


class DiscoveryService(Service):
    name = "discovery"
    leader_group_name = "discovery-%(pool)s"
    pooled = True
    require_nsq_writer = True
    process_name = "noc-%(name).10s-%(pool).5s"

    def __init__(self):
        super(DiscoveryService, self).__init__()
        self.send_callback = None

    @tornado.gen.coroutine
    def on_activate(self):
        slot_number, total_slots = yield self.acquire_slot()
        if total_slots > 1:
            self.logger.info(
                "Enabling distributed mode: Slot %d/%d",
                slot_number, total_slots
            )
            ifilter = {
                "key": {
                    "$mod": [
                        total_slots,
                        slot_number
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
            service=self
        )
        self.scheduler.run()

    def get_mon_data(self):
        r = super(DiscoveryService, self).get_mon_data()
        if self.scheduler:
            self.scheduler.apply_metrics(r)
        return r


if __name__ == "__main__":
    DiscoveryService().start()
