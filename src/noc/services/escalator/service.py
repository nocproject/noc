#!./bin/python
# ---------------------------------------------------------------------
# Escalator
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict

# NOC modules
from noc.config import config
from noc.core.scheduler.scheduler import Scheduler
from noc.core.service.base import BaseService
from noc.fm.models.ttsystem import DEFAULT_TTSYSTEM_SHARD, TTSystem


class EscalatorService(BaseService):
    name = "escalator"
    leader_lock_name = "escalator"
    use_telemetry = True
    use_mongo = True
    use_router = True

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.shards: dict[str, Scheduler] = {}

    async def on_activate(self) -> None:
        self.apply_shards()

    async def on_deactivate(self) -> None:
        for s in self.shards:
            self.logger.info("Shutting down shard %s", s)
            try:
                await self.shards[s].shutdown()
                self.logger.info("Shard %s is down", s)
            except TimeoutError:
                self.logger.info("Cannot shutdown shard %s cleanly: Timeout", s)

    def apply_shards(self) -> None:
        # Get shards settings
        shard_threads: defaultdict[str, int] = defaultdict(int)
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
