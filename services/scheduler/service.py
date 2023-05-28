#!./bin/python
# ----------------------------------------------------------------------
# Scheduler
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime

# NOC modules
from noc.config import config
from noc.core.scheduler.scheduler import Scheduler
from noc.core.service.fastapi import FastAPIService


class SchedulerService(FastAPIService):
    name = "scheduler"
    leader_lock_name = "scheduler"
    use_mongo = True
    use_router = True

    TOPOLOGY_JOB = "noc.services.scheduler.jobs.topology_uplinks.TopologyUplinksJob"

    async def on_activate(self):
        self.scheduler = Scheduler(
            "scheduler", reset_running=True, max_threads=config.scheduler.max_threads
        )
        self.scheduler.run()
        self.ensure_topology_job()

    @classmethod
    def ensure_topology_job(cls):
        """
        Create or remove Topology Scheduler job
        :return:
        """
        scheduler = Scheduler(cls.name)
        if config.topo.enable_scheduler_task:
            scheduler.submit(
                jcls=cls.TOPOLOGY_JOB, ts=datetime.datetime.now() + datetime.timedelta(seconds=60)
            )
            return
        scheduler.remove_job(jcls=cls.TOPOLOGY_JOB)


if __name__ == "__main__":
    SchedulerService().start()
