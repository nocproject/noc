#!./bin/python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Escalator
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict
# Third-party modules
import tornado.ioloop
import tornado.gen
# NOC modules
from noc.config import config
from noc.core.service.base import Service
from noc.core.scheduler.scheduler import Scheduler
from noc.fm.models.ttsystem import TTSystem, DEFAULT_TTSYSTEM_SHARD


class EscalatorService(Service):
    name = "escalator"
    leader_lock_name = "escalator"

    def __init__(self, *args, **kwargs):
        super(EscalatorService, self).__init__(*args, **kwargs)
        self.shards = {}

    @tornado.gen.coroutine
    def on_activate(self):
        self.apply_shards()

    @tornado.gen.coroutine
    def on_deactivate(self):
        for s in self.shards:
            self.logger.info("Shutting down shard %s", s)
            try:
                yield self.shards[s].shutdown()
                self.logger.info("Shard %s is down", s)
            except tornado.gen.TimeoutError:
                self.logger.info("Cannot shutdown shard %s cleanly: Timeout", s)

    def apply_shards(self):
        # Get shards settings
        shard_threads = defaultdict(int)
        shard_threads[DEFAULT_TTSYSTEM_SHARD] = config.escalator.max_threads
        for s in TTSystem.objects.all():
            if not s.is_active:
                continue
            shard_threads[s.shard_name] += s.max_threads
        # Run shard schedulers
        for sn in shard_threads:
            self.logger.info("Running shard %s (%d threads)",
                             sn, shard_threads[sn])
            self.shards[sn] = Scheduler(
                "escalator",
                pool=sn,
                reset_running=True,
                max_threads=shard_threads[sn],
                ioloop=self.ioloop,
                service=self
            )
            self.shards[sn].run()

if __name__ == "__main__":
    EscalatorService().start()
