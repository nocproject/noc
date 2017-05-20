#!./bin/python
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
        self.scheduler = None
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
            pool=self.config.pool,
            reset_running=True,
            max_threads=self.config.max_threads,
            ioloop=self.ioloop,
            filter=ifilter,
            use_cache=True
        )
        self.scheduler.service = self
        self.scheduler.run()

    def get_mon_data(self):
        r = super(DiscoveryService, self).get_mon_data()
        if self.scheduler:
            self.scheduler.apply_metrics(r)
        return r

    @tornado.gen.coroutine
    def on_deactivate(self):
        if self.scheduler:
            yield self.scheduler.shutdown()

if __name__ == "__main__":
    DiscoveryService().start()
