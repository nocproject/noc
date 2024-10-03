# ---------------------------------------------------------------------
# Runner implementation
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Iterator, Dict, Set, Optional, Any, Tuple
from logging import getLogger
import asyncio
from time import perf_counter_ns
import datetime

# Third-party modules
from bson import ObjectId

# NOC modules
from noc.core.debug import error_report
from noc.sa.models.job import JobStatus
from .models.jobreq import JobRequest
from .job import Job
from .lock import LockManager
from .actions.base import ActionError


logger = getLogger(__name__)


class Runner(object):
    """
    Job Runner.
    """

    def __init__(
        self,
        concurrency: int = 10,
        queue: Optional[asyncio.Queue[Tuple[Optional[ObjectId], Dict[str, Any]]]] = None,
    ):
        self._jobs: Dict[ObjectId, Job] = {}
        self._tasks: Set[asyncio.Task] = set()
        self._semaphore = asyncio.Semaphore(concurrency)
        self._status_lock = asyncio.Lock()
        self._locks = LockManager()
        self._queue = queue

    async def drain(self) -> None:
        """Wait until all task are complete."""
        while self._tasks:
            # await asyncio.wait(tuple(self._tasks))
            for task in asyncio.as_completed(tuple(self._tasks)):
                try:
                    await task
                except asyncio.CancelledError:
                    pass

    def iter_jobs(self) -> Iterator[Job]:
        """Iterate all jobs known to runner."""
        yield from self._jobs.values()

    def submit(self, req: JobRequest) -> None:
        """
        Submit new job group to runner.

        Args:
            req: Job request.
        """

        def iter_req(req: JobRequest) -> Iterator[JobRequest]:
            """
            Yields all nested job requests
            """
            yield req
            if req.jobs:
                for r in req.jobs:
                    yield from iter_req(r)

        j_map = {r.id: r for r in iter_req(req)}
        for job in Job.from_req(req):
            logger.info("[%s|%s] Submitted job", job.id, job.name)
            self.add_job(job)
            if self._queue is not None:
                self._save_new_job(job, j_map[str(job.id)])

    def add_job(self, job: Job) -> None:
        """
        Called when new job is instantiated.
        """
        self._jobs[job.id] = job
        if not job.has_children and not job.is_blocked():
            self._schedule_job(job)

    def _schedule_job(self, job: Job) -> None:
        """
        Submit job to run.
        """
        logger.info("[%s|%s] Sheduling to execution", job.id, job.name)
        task = asyncio.create_task(self.run_job(job.id))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        job.set_task(task)

    def _save_new_job(self, job: Job, req: JobRequest) -> None:
        """
        Send to persistent storage.
        """
        if not self._queue:
            return
        r: Dict[str, Any] = {
            "_id": job.id,
            "name": req.name,
            "parent": job.parent.id if job.parent else None,
            "description": req.description,
            "allow_fail": req.allow_fail,
            "status": job.status.value,
            "action": req.action or None,
            "inputs": (
                [{"name": i.name, "value": i.value, "job": i.job} for i in req.inputs]
                if req.inputs
                else None
            ),
            "locks": req.locks,
            "depends_on": [j.id for j in job.iter_depends_on()],
            "environment": req.environment or None,
            "created_at": datetime.datetime.now(),
        }
        self._queue.put_nowait((None, r))

    async def run_job(self, job_id: ObjectId) -> None:
        """
        Scheduled task.
        """
        async with self._semaphore:
            await self._run_job(job_id)

    async def _run_job(self, job_id: ObjectId) -> None:
        """
        Inner task runner
        """
        logger.info("[%s] Runing job", job_id)
        job = self._jobs.get(job_id)
        if not job:
            logger.info("[%s] Job is missed, skipping", job_id)
            return
        # Jobs can be started only from WAITING
        if not job.is_waiting:
            logger.info("[%s|%s] Job status is %s, skipping", job.id, job.name, job.status)
            return
        # Check if job is not blocked by parents.
        if job.is_blocked_by_parents():
            logger.info("[%s|%s] is blocked by parents, skipping", job.id, job.name)
        # Set job status
        self.set_status(job, JobStatus.RUNNING)
        # Run parents if necessary
        for p in job.iter_parents():
            if p.is_waiting:
                self.set_status(p, JobStatus.RUNNING)
        # Process job logs
        # Run job
        t0 = perf_counter_ns()
        locks = list(job.iter_lock_names())
        try:
            if locks:
                logger.info("[%s|%s] Acquiring locks: %s", job.id, job.name, ", ".join(locks))
            async with self._locks.acquire(locks):
                if locks:
                    logger.info("[%s|%s] All locks are aquired", job.id, job.name)
                await job.run()
            status = JobStatus.SUCCESS
        except asyncio.TimeoutError:
            logger.error("[%s|%s] Timed out", job.id, job.name)
            status = JobStatus.WARNING if job.allow_fail else JobStatus.CANCELLED
        except asyncio.CancelledError:
            logger.error("[%s] Cancelled", job.id, job.name)
            status = JobStatus.CANCELLED
        except ActionError as e:
            logger.error("[%s|%s] Error: %s", job.id, job.name, e)
            status = JobStatus.WARNING if job.allow_fail else JobStatus.FAILED
        except Exception:
            error_report()
            status = JobStatus.WARNING if job.allow_fail else JobStatus.FAILED
        finally:
            dt = perf_counter_ns() - t0
            logger.info("[%s|%s] executed in %d ms", job.id, job.name, dt / 1_000_000)
        self.set_status(job, status)
        job.set_task(None)
        await self.apply_group(job)
        self.prune_jobs(job)

    def prune_jobs(self, job: "Job") -> None:
        """
        Remove all jobs
        """
        leader = job.leader
        if not leader.is_complete:
            return
        for j in leader.iter_group():
            if j.id in self._jobs:
                logger.info("[%s|%s] Pruning job", j.id, j.name)
                del self._jobs[j.id]

    async def apply_group(self, job: Job) -> None:
        """
        Modify group state depending on job result.
        """
        async with self._status_lock:
            if job.is_complete_failed:
                self.check_group_fail(job)
            else:
                self.check_group_success(job)

    def check_group_success(self, job: Job) -> None:
        """
        Try to finish group.
        """
        # Unblock siblings
        for s in job.iter_siblings():
            if s.is_waiting and not s.is_scheduled and not s.is_blocked():
                self._schedule_job(s)
        #
        p = job.parent
        if not p or p.is_complete:
            return
        if not p.is_running:
            return
        if any(True for c in p.iter_children() if not c.is_complete):
            return  # Incomplete jobs
        # All jobs are complete
        # Note, that fails are processed by cancel_group()
        # so we skip this case here
        fail = any(True for c in p.iter_children() if not c.is_complete_success)
        if not fail:
            self.set_status(p, JobStatus.SUCCESS)
            self.check_group_success(p)

    def check_group_fail(self, job: Job) -> None:
        """
        Cancel whole group of the job.
        """

        def cancel_down(job: Job) -> None:
            for c in job.iter_children():
                if not c.is_complete:
                    self.set_status(c, JobStatus.CANCELLED)
                    cancel_down(c)

        def cancel_siblings(job: Job) -> None:
            for s in job.iter_siblings():
                if not s.is_complete:
                    self.set_status(s, JobStatus.CANCELLED)
                    cancel_down(s)

        def error_up(job: Job) -> None:
            p = job.parent
            if not p or p.is_complete:
                return
            if p.allow_fail:
                self.set_status(p, JobStatus.WARNING)
                self.check_group_success(p)
            else:
                self.set_status(p, job.status)
                self.check_group_fail(p)

        cancel_down(job)
        cancel_siblings(job)
        error_up(job)

    def set_status(self, job: Job, status: JobStatus) -> None:
        """
        Set job's status.
        """
        if job.status == status:
            return
        logger.info(
            "[%s|%s] Status change %s -> %s", job.id, job.name, job.status.name, status.name
        )
        job.status = status
        if self._queue:
            # Store
            r: Dict[str, Any] = {"status": job.status.value}
            if job.is_running:
                r["started_at"] = datetime.datetime.now()
            elif job.is_complete:
                r["completed_at"] = datetime.datetime.now()
                if job.parent:
                    parent = job.parent
                    if parent.environment.is_dirty:
                        # Update environment
                        r["environment"] = parent.environment.raw_data()
                        parent.environment.clear_dirty()
                    if parent.is_dirty_result:
                        # Update results
                        r["results"] = parent.results_json()
                        parent.clear_dirty_result()
            self._queue.put_nowait((job.id, r))
        if job.is_cancelled:
            job.cancel()
