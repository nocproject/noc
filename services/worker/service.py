# ----------------------------------------------------------------------
# worker service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import orjson

# NOC modules
from noc.core.service.fastapi import FastAPIService
from noc.core.liftbridge.message import Message
from noc.core.handler import get_handler
from noc.core.debug import error_report


class WorkerService(FastAPIService):
    name = "worker"
    use_mongo = True

    def __init__(self):
        super().__init__()
        self.slot_number = 0
        self.total_slots = 0

    async def on_activate(self):
        self.slot_number, self.total_slots = await self.acquire_slot()
        await self.subscribe_stream("jobs", self.slot_number, self.on_job)

    async def on_job(self, msg: Message):
        self.logger.debug("[%s|%s] New job", msg.partition, msg.offset)
        # Decode job
        try:
            data = orjson.loads(msg.value)
        except ValueError as e:
            self.logger.error("[%s|%s] Cannot decode JSON: %s", msg.partition, msg.offset, e)
            return
        # Convert job to a list of jobs
        if isinstance(data, dict):
            data = [data]
        # Execute functions one by one
        for f in data:
            # Get function
            path = f.get("handler")
            if not path:
                self.logger.error(
                    "[%s|%s] No handler in %r. Skipping", msg.partition, msg.offset, f
                )
                continue
            try:
                fn = get_handler(path)
            except ImportError:
                self.logger.error(
                    "[%s|%s] Invalid handler %s. Skipping", msg.partition, msg.offset, path
                )
                continue
            # Call function
            self.logger.debug("[%s|%s] Calling %s", msg.partition, msg.offset, path)
            try:
                kwargs = f.get("kwargs") or {}
                r = fn(**kwargs)
                self.logger.debug("[%s|%s] Returned: %r", msg.partition, msg.offset, r)
            except Exception:
                self.logger.debug("[%s|%s] Failed", msg.partition, msg.offset)
                error_report()
                continue
            self.logger.debug("[%s|%s] Done", msg.partition, msg.offset)
        self.logger.debug("[%s|%s] Complete", msg.partition, msg.offset)


if __name__ == "__main__":
    WorkerService().start()
