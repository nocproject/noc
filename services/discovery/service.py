#!./bin/python
# ----------------------------------------------------------------------
# Discovery
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.config import config
from noc.core.scheduler.scheduler import Scheduler
from noc.core.scheduler.job import Job
from noc.core.service.fastapi import FastAPIService


class DiscoveryService(FastAPIService):
    name = "discovery"
    pooled = True
    use_mongo = True
    use_router = True
    process_name = "noc-%(name).10s-%(pool).5s"

    def __init__(self):
        super().__init__()
        self.send_callback = None
        self.slot_number = 0
        self.total_slots = 0

    async def on_activate(self):
        self.slot_number, self.total_slots = await self.acquire_slot()
        if self.total_slots > 1:
            self.logger.info(
                "Enabling distributed mode: Slot %d/%d", self.slot_number, self.total_slots
            )
            # ifilter = {"key": {"$mod": [self.total_slots, self.slot_number]}}
            ifilter = {"shard": self.slot_number}
        else:
            self.logger.info("Enabling standalone mode")
            ifilter = None
        self.scheduler = Scheduler(
            "discovery",
            pool=config.pool,
            reset_running=True,
            max_threads=config.discovery.max_threads,
            check_time=config.discovery.job_check_interval,
            filter=ifilter,
            service=self,
            sample=config.discovery.sample,
            ignore_import_errors=True,
        )
        # Ensure shard
        if ifilter:
            self.logger.info("Ensure shard field on collection")
            coll = self.scheduler.get_collection()
            coll.update_many(
                {
                    Job.ATTR_KEY: {"$mod": [self.total_slots, self.slot_number]},
                    Job.ATTR_SHARD: {"$ne": self.slot_number},
                },
                {"$set": {Job.ATTR_SHARD: self.slot_number}},
            )
        # Run scheduler
        self.scheduler.run()

    def get_mon_data(self):
        r = super().get_mon_data()
        if self.scheduler:
            self.scheduler.apply_metrics(r)
        return r


if __name__ == "__main__":
    DiscoveryService().start()
