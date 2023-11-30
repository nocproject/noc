# ---------------------------------------------------------------------
# Runner implementation
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Iterator, Dict, Set
from logging import getLogger
import asyncio
from time import perf_counter_ns

# Third-party modules
from bson import ObjectId

# NOC modules
from noc.core.debug import error_report
from noc.sa.models.job import JobStatus
from .models.jobreq import JobRequest
from .job import Job
from .actions.base import ActionError


logger = getLogger(__name__)


class Runner(object):
    """
    Job Runner.
    """

    def __init__(self, concurrency: int = 10):
        self._jobs: Dict[ObjectId, Job] = {}
        self._tasks: Set[asyncio.Task] = set()
        self._semaphore = asyncio.Semaphore(concurrency)
        self._status_lock = asyncio.Lock()

    async def drain(self) -> None:
        """Wait until all task complete."""
        while self._tasks:
            await asyncio.wait(tuple(self._tasks))

    def iter_jobs(self) -> Iterator[Job]:
        """Iterate all jobs known to runner."""
        yield from self._jobs.values()

    def submit(self, req: JobRequest) -> None:
        """
        Submit new job to runner.

        Args:
            req: Job request.
        """
        for job in Job.from_req(req):
            logger.info("[%s] Submitted job", job)
            self._on_new_job(job)

    def _on_new_job(self, job: Job) -> None:
        """
        Called when new job is instantiated.
        """
        self._jobs[job.id] = job
        if not job.is_leader and not job.is_blocked():
            self._schedule_job(job)

    def _schedule_job(self, job: Job) -> None:
        logger.info("[%s] Sheduling to execution", job)
        task = asyncio.create_task(self.run_job(job.id))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        job.set_task(task)

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
        if job.status != JobStatus.WAITING:
            logger.info("[%s] Job status is %s, skipping", job, job.status)
            return
        # Check if job is not blocked by parents.
        if job.is_blocked_by_parents():
            logger.info("[%s] is blocked by parents, skipping", job)
        # or waiting and not blocked by their siblings
        # @todo: Parse arguments
        # Set job status
        self.set_status(job, JobStatus.RUNNING)
        # Run parents if necessary
        for p in job.iter_parents():
            if p.is_waiting:
                self.set_status(p, JobStatus.RUNNING)
        # Run job
        t0 = perf_counter_ns()
        try:
            await job.run()
            status = JobStatus.SUCCESS
        except asyncio.TimeoutError:
            logger.error("[%s] Timed out", job)
            status = JobStatus.WARNING if job.allow_fail else JobStatus.CANCELLED
        except asyncio.CancelledError:
            logger.error("[%s] Cancelled", job)
            status = JobStatus.CANCELLED
        except ActionError as e:
            logger.error("[%s] Error: %s", job, e)
            status = JobStatus.WARNING if job.allow_fail else JobStatus.FAILED
        except Exception:
            error_report()
            status = JobStatus.WARNING if job.allow_fail else JobStatus.FAILED
        finally:
            dt = perf_counter_ns() - t0
            logger.info("[%s] executed in %d ms", job, dt / 1_000_000)
        self.set_status(job, status)
        await self.apply_group(job)

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
        if p.status != JobStatus.RUNNING:
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
                self.update_group(p)
            else:
                self.set_status(p, job.status)
                self.check_group_fail(p)

        cancel_down(job)
        cancel_siblings(job)
        error_up(job)

    def set_status(self, job: Job, status: JobStatus) -> None:
        if job.status == status:
            return
        logger.info("[%s] Status change %s -> %s", job, job.status.name, status.name)
        job.status = status
        if status == JobStatus.CANCELLED:
            job.cancel()
