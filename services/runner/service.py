#!./bin/python
# ----------------------------------------------------------------------
# runner service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import asyncio
from typing import Optional, Dict, Any, Tuple, DefaultDict, List
from time import perf_counter_ns
from collections import defaultdict

# Third-party modules
import orjson
from pydantic import TypeAdapter, ValidationError
from bson import ObjectId
from pymongo import InsertOne, UpdateOne

# NOC modules
from noc.core.service.fastapi import FastAPIService
from noc.core.msgstream.message import Message
from noc.core.perf import metrics
from noc.core.runner.runner import Runner
from noc.core.runner.job import Job
from noc.core.mongo.connection_async import get_db, connect_async
from noc.config import config
from noc.sa.models.job import JobStatus
from noc.services.runner.models.runnerreq import RunnerRequest, JobRequest
from noc.core.debug import ErrorReport

ta_RunnerRequest = TypeAdapter(RunnerRequest)
STREAM = "submit"


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
        self.runner = Runner(concurrency=config.runner.max_running, queue=self.queue)
        asyncio.create_task(self.sync_task())
        await self.subscribe_stream(STREAM, self.slot_number, self.on_msg)

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
        op = req.op or "submit"
        msg_handler = getattr(self, f"on_msg_{op}")
        if not msg_handler:
            self.logger.error("Internal error. No handler for '%s'", req.op)
            return
        try:
            with ErrorReport(logger=self.logger):
                await msg_handler(req)
        except Exception:
            self.logger.info("Recovering from error")

    async def on_msg_submit(self, req: JobRequest) -> None:
        try:
            metrics["submits"] += 1
            self.runner.submit(req)
        except ValueError as e:
            self.logger.error("Failed to submit job: %s", e)
            metrics["failed_submits"] += 1

    async def sync_task(self):
        while True:
            try:
                with ErrorReport(logger=self.logger):
                    await self._sync_task()
            except Exception:
                self.logger.error("Recovering from error")

    async def _sync_task(self):
        """Save state chages to database (implementaion)"""
        coll = get_db()["jobs"]
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

    async def restore_state(self):
        def create_job(doc: Dict[str, Any]) -> Job:
            job = Job.from_dict(doc, jmap=jobs)
            jobs[job.id] = job
            # Release blocked jobs
            if job.id in blocks:
                for j_id in blocks[job.id]:
                    jdoc = blocked[j_id]
                    if not any(j not in jobs for j in jdoc["depends_on"]):
                        create_job(jdoc)
                        del blocked[j_id]
                del blocks[job.id]
            return job

        if self.runner is None:
            return
        coll = get_db()["jobs"]
        t0 = perf_counter_ns()
        self.logger.info("Restoring state")
        # Find non-complete leaders
        jobs: Dict[ObjectId, Job] = {}
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
            create_job(doc)
        # Find all children
        blocked: Dict[ObjectId, Dict[str, Any]] = {}
        blocks: DefaultDict[ObjectId, List[ObjectId]] = defaultdict(list)
        wave = list(jobs)
        while wave:
            new_wave: List[ObjectId] = []
            async for doc in coll.find({"parent": {"$in": wave}}):
                depends_on: List[ObjectId] = doc.get("depends_on") or []
                if not depends_on:
                    # Not blocked, no dependencies
                    create_job(doc)
                else:
                    is_blocked = False
                    for j in depends_on:
                        if j not in jobs:
                            is_blocked = True
                            blocks[j] = doc["_id"]
                    if is_blocked:
                        blocked[doc["_id"]] = doc
                    else:
                        create_job(doc)
                # Prepare next wave
                new_wave.append(doc["_id"])
            wave = new_wave
        if blocked or blocks:
            self.logger.error("There are %d jobs unprocessed", max(len(blocks), len(blocked)))
        for job in jobs.values():
            self.runner.add_job(job)
        dt = perf_counter_ns() - t0
        self.logger.info("%d jobs restored in %.2fms", len(jobs), float(dt) / 1_000_000.0)


if __name__ == "__main__":
    RunnerService().start()
