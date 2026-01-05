#!./bin/python
# ----------------------------------------------------------------------
# Scheduler
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
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

    SYNC_PURGATORIUM_JOB = "noc.services.scheduler.jobs.sync_purgatorium.SyncPurgatoriumJob"

    NETWORK_INSTANCE_DISCOVERY_JOB = (
        "noc.services.scheduler.jobs.network_instance_service.NetworkInstanceDiscoveryJob"
    )

    async def on_activate(self):
        self.scheduler = Scheduler(
            "scheduler", reset_running=True, max_threads=config.scheduler.max_threads
        )
        self.scheduler.run()
        self.ensure_topology_job()
        self.ensure_purgatorium_job()
        self.ensure_network_instance_discovery_job()
        self.ensure_watchers_job()

    @classmethod
    def ensure_topology_job(cls):
        """Create or remove Topology Scheduler job"""
        scheduler = Scheduler(cls.name)
        if config.topo.enable_scheduler_task:
            scheduler.submit(
                jcls=cls.TOPOLOGY_JOB, ts=datetime.datetime.now() + datetime.timedelta(seconds=60)
            )
            return
        scheduler.remove_job(jcls=cls.TOPOLOGY_JOB)

    @classmethod
    def ensure_purgatorium_job(cls):
        """Create or remove Purgatorium Scheduler job"""
        scheduler = Scheduler(cls.name)
        scheduler.submit(
            jcls=cls.SYNC_PURGATORIUM_JOB,
            ts=datetime.datetime.now() + datetime.timedelta(seconds=60),
        )

    @classmethod
    def ensure_network_instance_discovery_job(cls):
        """Create find Service Instance Job"""
        scheduler = Scheduler(cls.name)
        scheduler.submit(
            jcls=cls.NETWORK_INSTANCE_DISCOVERY_JOB,
            ts=datetime.datetime.now() + datetime.timedelta(seconds=60),
        )

    @classmethod
    def ensure_watchers_job(cls):
        """Create watchers job"""
        from noc.core.watchers.decorator import WATCHER_JCLS

        scheduler = Scheduler(cls.name)
        scheduler.submit(jcls=WATCHER_JCLS, key="sa.Service", keep_ts=True)
        scheduler.submit(jcls=WATCHER_JCLS, key="sa.ManagedObject", keep_ts=True)


if __name__ == "__main__":
    SchedulerService().start()
