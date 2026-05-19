#!./bin/python
# ---------------------------------------------------------------------
# Escalator
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import asyncio
from collections import defaultdict
from time import perf_counter_ns
from typing import Optional, Dict, Any, Tuple, DefaultDict

# Third-party modules
from bson import ObjectId
from pymongo import InsertOne, UpdateOne

# NOC modules
from noc.config import config
from noc.core.scheduler.scheduler import Scheduler
from noc.core.service.fastapi import FastAPIService
from noc.core.debug import ErrorReport
from noc.core.perf import metrics
from noc.fm.models.ttsystem import TTSystem, DEFAULT_TTSYSTEM_SHARD
from noc.services.escalator.runner import EscalationRunner
from noc.fm.models.escalationjob import EscalationJob
from noc.services.escalator.job import AlarmAutomationJob


class EscalatorService(FastAPIService):
    name = "escalator"
    leader_lock_name = "escalator"
    use_telemetry = True
    use_mongo = True
    use_router = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shards: Dict[str, Scheduler] = {}
        self.queue: asyncio.Queue[Tuple[Optional[ObjectId], Dict[str, Any]]] = asyncio.Queue()
        self.runner: Optional[EscalationRunner] = None

    async def on_activate(self):
        self.apply_shards()
        self.runner = EscalationRunner(concurrency=config.runner.max_running, queue=self.queue)
        asyncio.create_task(self.sync_task())

    async def on_deactivate(self):
        for s in self.shards:
            self.logger.info("Shutting down shard %s", s)
            try:
                await self.shards[s].shutdown()
                self.logger.info("Shard %s is down", s)
            except asyncio.TimeoutError:
                self.logger.info("Cannot shutdown shard %s cleanly: Timeout", s)

    async def sync_task(self):
        while True:
            try:
                with ErrorReport(logger=self.logger):
                    await self._sync_task()
            except Exception:
                self.logger.error("Recovering from error")

    async def _sync_task(self):
        """Save state chages to database (implementaion)"""
        coll = EscalationJob._get_collection()
        while True:
            # Get changes
            bulk = []
            while not self.queue.empty():
                job_id, data = self.queue.get_nowait()
                if job_id:
                    # Update
                    bulk.append(UpdateOne({"_id": job_id}, {"$set": data}))
                else:
                    # Insert
                    bulk.append(InsertOne(data))
            if bulk:
                self.logger.debug("Writing %s changes", len(bulk))
                t0 = perf_counter_ns()
                await coll.bulk_write(bulk)
                dt = perf_counter_ns() - t0
                self.logger.debug(
                    "%d changes written in %.2fms", len(bulk), float(dt) / 1_000_000.0
                )
                metrics["sync_changes"] += len(bulk)
            await asyncio.sleep(1.0)

    def apply_shards(self):
        # Get shards settings
        shard_threads: DefaultDict[str, int] = defaultdict(int)
        shard_threads[DEFAULT_TTSYSTEM_SHARD] = config.escalator.max_threads
        for s in TTSystem.objects.all():
            if not s.is_active:
                continue
            shard_threads[s.shard_name] += s.max_threads
        # Run shard schedulers
        for sn in shard_threads:
            self.logger.info("Running shard %s (%d threads)", sn, shard_threads[sn])
            self.shards[sn] = Scheduler(
                "escalator",
                pool=sn,
                reset_running=True,
                max_threads=shard_threads[sn],
                check_time=config.escalator.job_check_interval,
                service=self,
                sample=config.escalator.sample,
            )
            self.shards[sn].run()


if __name__ == "__main__":
    EscalatorService().start()
