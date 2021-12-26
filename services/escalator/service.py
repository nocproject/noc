#!./bin/python
# ---------------------------------------------------------------------
# Escalator
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict
import asyncio
from typing import Dict, DefaultDict

# NOC modules
from noc.config import config
from noc.core.service.tornado import TornadoService
from noc.core.scheduler.scheduler import Scheduler
from noc.fm.models.ttsystem import TTSystem, DEFAULT_TTSYSTEM_SHARD


class EscalatorService(TornadoService):
    name = "escalator"
    leader_lock_name = "escalator"
    use_telemetry = True
    use_mongo = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shards: Dict[str, Scheduler] = {}

    async def on_activate(self):
        self.apply_shards()

    async def on_deactivate(self):
        for s in self.shards:
            self.logger.info("Shutting down shard %s", s)
            try:
                await self.shards[s].shutdown()
                self.logger.info("Shard %s is down", s)
            except (asyncio.TimeoutError, asyncio.exceptions.TimeoutError):
                self.logger.info("Cannot shutdown shard %s cleanly: Timeout", s)

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
                service=self,
                sample=config.escalator.sample,
            )
            self.shards[sn].run()


if __name__ == "__main__":
    EscalatorService().start()
