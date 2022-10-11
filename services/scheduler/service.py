#!./bin/python
# ----------------------------------------------------------------------
# Scheduler
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.config import config
from noc.core.scheduler.scheduler import Scheduler
from noc.core.service.fastapi import FastAPIService


class SchedulerService(FastAPIService):
    name = "scheduler"
    leader_lock_name = "scheduler"
    use_mongo = True
    use_router = True

    async def on_activate(self):
        self.scheduler = Scheduler(
            "scheduler", reset_running=True, max_threads=config.scheduler.max_threads
        )
        self.scheduler.run()


if __name__ == "__main__":
    SchedulerService().start()
