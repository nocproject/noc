#!./bin/python
# ----------------------------------------------------------------------
# runner service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import asyncio
from typing import Optional, Dict, Any, Tuple
from time import perf_counter_ns

# Third-party modules
import orjson
from pydantic import TypeAdapter, ValidationError
from bson import ObjectId
from pymongo import InsertOne, UpdateOne

# NOC modules
from noc.core.service.fastapi import FastAPIService
from noc.core.msgstream.message import Message
from noc.core.handler import get_handler
from noc.core.debug import error_report
from noc.core.perf import metrics
from noc.core.runner.runner import Runner
from noc.core.mongo.connection_async import get_db
from noc.config import config
from noc.sa.models.job import JobStatus
from noc.services.runner.models.runnerreq import RunnerRequest, JobRequest

ta_RunnerRequest = TypeAdapter(RunnerRequest)


class RunnerService(FastAPIService):
    name = "runner"
    use_mongo = True

    def __init__(self):
        super().__init__()
        self.slot_number = 0
        self.total_slots = 0
        self.queue: asyncio.Queue[Tuple[Optional[ObjectId], Dict[str, Any]]] = asyncio.Queue()
        self.runner: Optional[Runner] = None

    async def on_activate(self):
        connect_async()
        self.runner = Runner(concurrency=config.runner.max_jobs, queue=self.queue)
        await self.subscribe_stream("runner", self.slot_number, self.on_msg)

    async def on_msg(self, msg: Message):
        metrics["requests"] += 1
        data: Dict[str, Any] = orjson.loads(msg.value)
        # Parse request
        try:
            req = ta_RunnerRequest.validate_python(data)
        except ValidationError as e:
            self.logger.error("Malformed message: %s", e)
            metrics["malformed_messages"] += 1
            return
        # Call handler, may not be invalid
        msg_handler = getattr(self, f"on_msg_{req.op}")
        if not msg_handler:
            self.logger.error("Internal error. No handler for '%s'", req.op)
            return
        await msg_handler(req)

    async def on_msg_submit(req: JobRequest) -> None:
        try:
            metrics["submits"] += 1
            self.runner.submit(req)
        except ValueError as e:
            self.logger.error("Failed to submit job: %s", e)
            metrics["failed_submits"] += 1

    async def sync_task(self):
        """Save state chages to database"""
        coll = get_db()["jobs"]
        while True:
            # Get changes
            bulk = []
            while not self.queue.empty():
                job_id, data = self.queue.get_nowait()
                if job_id:
                    # Update
                    bulk.append(UpdateOne({"_id": job_id}, data))
                else:
                    # Insert
                    bulk.append(InsertOne(data))
            if bulk:
                self.logger.debug("Writing %s changes", len(bulk))
                t0 = perf_counter_ns()
                await coll.bulk_write(bulk)
                dt = t0 - perf_counter_ns()
                self.logger.debug("%d changes written in %.2fms", float(dt) / 1_000_000.0)
                metrics["sync_changes"] += len(bulk)
            asyncio.sleep(1.0)

    async def restore_state(self):
        coll = get_db()["jobs"]
        perf_counter_ns()
        self.logger.info("Restoring state")
        # Find non-complete leaders
        jobs = {}
        async for doc in coll.find(
            {
                "parent": None,
                "status": {
                    "$nin": [
                        JobStatus.SUCCESS.value,
                        JobStatus.WARNING.value,
                        JobStatus.FAILED.value,
                        JobStatus.CANCELLED.value,
                    ]
                },
            }
        ):
            jobs[doc["_id"]] = doc
        # Find all children
        wave = list(jobs)
        while wave:
            new_wave = []
            async for doc in coll.find({"parent": {"$in": wave}}):
                jobs[doc["_id"]] = doc
                new_wave.append(doc["_id"])
            wave = new_wave


if __name__ == "__main__":
    RunnerService().start()
