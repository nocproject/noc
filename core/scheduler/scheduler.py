# ----------------------------------------------------------------------
# Scheduler Job Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import datetime
import random
import threading
import time
import asyncio
from time import perf_counter
from typing import List, Optional

# Third-party modules
import pymongo.errors
from pymongo import DeleteOne, UpdateOne

# NOC modules
from noc.core.mongo.connection import get_db
from noc.core.handler import get_handler
from noc.core.threadpool import ThreadPoolExecutor
from noc.core.perf import metrics
from noc.config import config
from .job import Job


class Scheduler(object):
    COLLECTION_BASE = "noc.schedules."

    SUBMIT_THRESHOLD_FACTOR = config.scheduler.submit_threshold_factor
    MAX_CHUNK_FACTOR = config.scheduler.max_chunk_factor
    UPDATES_PER_CHECK = config.scheduler.updates_per_check

    CACHE_DEFAULT_TTL = config.scheduler.cache_default_ttl

    def __init__(
        self,
        name,
        pool=None,
        reset_running=False,
        max_threads=5,
        check_time=1000,
        submit_threshold=None,
        max_chunk=None,
        filter=None,
        service=None,
        sample=0,
        ignore_import_errors: bool = False,
    ):
        """
        Create scheduler.

        :param name: Unique scheduler name
        :param pool: Pool name, if run in pooled mode
        :param reset_running: Reset all running jobs to
            wait state on start
        :param max_threads: Thread executor threads
        :param check_time: time in milliseconds to check for new jobs
        :param max_chunk: Maximum amount of jobs which can be submitted
            at one step
        :param submit_threshold: Maximal executor queue length
            when submitting of next chunk is allowed
        :param filter: Additional filter to be applied to
            pending jobs
        :param sample: Tracing sample rate. 0 - do not sample,
           1 - sample every job
           N > 1 - sample very Nth job
        :param ignore_import_error: Do not remove job if caused import error.
        """
        self.logger = logging.getLogger("scheduler.%s" % name)
        self.name = name
        self.collection_name = self.COLLECTION_BASE + self.name
        self.pool = pool
        if pool:
            self.collection_name += ".%s" % pool
        self.to_reset_running = reset_running
        self.running_groups = set()
        self.collection = None
        self.bulk = []
        self.bulk_lock = threading.Lock()
        self.max_threads = max_threads
        self.executor: Optional[ThreadPoolExecutor] = None
        self.run_callback = None
        self.check_time = check_time
        self.read_ahead_interval = datetime.timedelta(milliseconds=check_time)
        if submit_threshold:
            self.submit_threshold = submit_threshold
        else:
            self.submit_threshold = max(self.max_threads // self.SUBMIT_THRESHOLD_FACTOR, 1)
        if max_chunk:
            self.max_chunk = max_chunk
        else:
            self.max_chunk = max(self.max_threads // self.MAX_CHUNK_FACTOR, 2)
        self.filter = filter
        self.to_shutdown = False
        self.min_sleep = float(check_time) / self.UPDATES_PER_CHECK / 1000.0
        self.jobs_burst = []
        self.cache = None
        self.cache_lock = threading.Lock()
        self.cache_set_ops = {}
        self.service = service
        if self.service:
            self.scheduler_id = "%s[%s:%s]" % (
                self.service.service_id,
                self.service.address,
                self.service.port,
            )
        else:
            self.scheduler_id = "standalone scheduler"
        self.sample = sample
        self.ignore_import_errors = ignore_import_errors

    def get_cache(self):
        with self.cache_lock:
            if not self.cache:
                from noc.core.cache.base import cache

                self.cache = cache
            return self.cache

    def run(self):
        """
        Run scheduler. Common usage

        scheduler.run()
        """
        reset_statuses = []
        if self.to_reset_running:
            reset_statuses.append(Job.S_RUN)
        if self.ignore_import_errors:
            reset_statuses.append(Job.S_POSTPONED)
        if reset_statuses:
            self.reset_to_waiting(reset_statuses)
        self.ensure_indexes()
        self.logger.info("Running scheduler")
        asyncio.create_task(self.scheduler_loop())

    def get_collection(self):
        """
        Returns mongo collection instance
        """
        if self.collection is None:
            self.logger.debug("Open collection %s", self.collection_name)
            self.collection = get_db()[self.collection_name]
            self.bulk = []
        return self.collection

    def get_executor(self) -> ThreadPoolExecutor:
        """
        Returns threadpool executor
        """
        if not self.executor:
            self.logger.debug("Run thread executor (%d threads)", self.max_threads)
            self.executor = ThreadPoolExecutor(self.max_threads, name=self.name)
        return self.executor

    def reset_to_waiting(self, statuses: List[str]) -> None:
        """
        Reset all running jobs to waiting status
        """
        self.logger.debug("Reset jobs")
        r = self.get_collection().update_many(
            self.get_query({Job.ATTR_STATUS: {"$in": statuses}}),
            {"$set": {Job.ATTR_STATUS: Job.S_WAIT}},
        )
        if r.acknowledged:
            if r.modified_count:
                self.logger.info("Reset: %d", r.modified_count)
            else:
                self.logger.info("Nothing to reset")
        else:
            self.logger.info("Failed to reset jobs")

    def suspend_keys(self, keys: List[int], suspend: bool = True):
        self.logger.debug("Suspend jobs")
        r = self.get_collection().update_many(
            self.get_query({Job.ATTR_KEY: {"$in": keys}}),
            {"$set": {Job.ATTR_STATUS: Job.S_SUSPEND if suspend else Job.S_WAIT}},
        )
        if r.acknowledged:
            if r.modified_count:
                self.logger.info("Suspend: %d", r.modified_count)
            else:
                self.logger.info("Nothing to suspend")
        else:
            self.logger.info("Failed to suspend jobs")

    def ensure_indexes(self):
        """
        Create all nesessary indexes
        """
        self.logger.debug("Check indexes")
        self.get_collection().create_index([("ts", 1)], partialFilterExpression={"s": "W"})
        self.get_collection().create_index(
            [("ts", 1), ("shard", 1)], partialFilterExpression={"s": "W"}
        )
        self.get_collection().create_index([("jcls", 1)])
        self.get_collection().create_index([("key", 1)])
        self.logger.debug("Indexes are ready")

    def get_query(self, q):
        """
        Combine filter with query and return resulting query
        """
        if self.filter:
            qq = self.filter.copy()
            qq.update(q)
            return qq
        return q

    def scheduler_tick(self):
        """
        Process single scheduler tick
        :return:
        """
        n = 0
        try:
            n = self.run_pending()
        except Exception as e:
            self.logger.error("Failed to schedule next tasks: %s", e)
        self.apply_ops()
        return n

    def apply_ops(self):
        self.apply_bulk_ops()
        self.apply_cache_ops()

    async def scheduler_loop(self):
        """
        Primary scheduler loop
        """
        while not self.to_shutdown:
            t0 = perf_counter()
            n = 0
            executor = self.get_executor()
            if executor.may_submit():
                try:
                    n = await executor.submit(self.scheduler_tick)
                except Exception as e:
                    self.logger.error("Failed to execute scheduler tick: %s", e)
            dt = self.check_time - (perf_counter() - t0) * 1000
            if dt > 0:
                if n:
                    dt = min(dt, self.check_time / n)
                await asyncio.sleep(dt / 1000.0)
        self.apply_ops()

    def iter_pending_jobs(self, limit):
        """
        Yields pending jobs
        """
        qs = (
            self.get_collection()
            .find(
                self.get_query(
                    {
                        Job.ATTR_TS: {"$lte": datetime.datetime.now() + self.read_ahead_interval},
                        Job.ATTR_STATUS: Job.S_WAIT,
                    }
                )
            )
            .limit(limit)
            .sort(Job.ATTR_TS)
        )
        try:
            for job in qs:
                job[Job.ATTR_SAMPLE] = self.sample
                try:
                    jcls = get_handler(job[Job.ATTR_CLASS])
                    yield jcls(self, job)
                except ImportError as e:
                    self.logger.error("Invalid job class %s", job[Job.ATTR_CLASS])
                    self.logger.error("Error: %s", e)
                    if self.ignore_import_errors:
                        self.postpone_job(job[job.ATTR_ID])
                    else:
                        self.remove_job_by_id(job[Job.ATTR_ID])
        except pymongo.errors.CursorNotFound:
            self.logger.info("Server cursor timed out. Waiting for next cycle")
        except pymongo.errors.OperationFailure as e:
            self.logger.error("Operation failure: %s", e)
            self.logger.error("Trying to recover")
        except pymongo.errors.AutoReconnect:
            self.logger.error("Auto-reconnect detected. Waiting for next cycle")

    def run_pending(self):
        """
        Read and launch all pending jobs
        """
        executor = self.get_executor()
        collection = self.get_collection()
        n = 0
        if not executor.may_submit():
            return 0
        jobs, self.jobs_burst = self.jobs_burst, []
        burst_ids = set(j.attrs[Job.ATTR_ID] for j in jobs)
        if len(jobs) <= self.max_chunk // 2:
            jobs += [
                j
                for j in self.iter_pending_jobs(self.max_chunk)
                if j.attrs[Job.ATTR_ID] not in burst_ids
            ]
        while jobs:
            free_workers = executor.get_free_workers()
            if not free_workers:
                self.logger.info("All workers are busy. Sending %d jobs to burst", len(jobs))
                self.jobs_burst = jobs
                break
            now = datetime.datetime.now()
            rl = min(sum(1 for j in jobs if j.attrs[Job.ATTR_TS] <= now), free_workers)
            rjobs, jobs = jobs[:rl], jobs[rl:]
            if rjobs:
                jids = [j.attrs[Job.ATTR_ID] for j in rjobs]
                self.logger.debug(
                    "update({_id: {$in: %s}}, {$set: {%s: '%s'}})", jids, Job.ATTR_STATUS, Job.S_RUN
                )
                r = collection.update_many(
                    {"_id": {"$in": jids}}, {"$set": {Job.ATTR_STATUS: Job.S_RUN}}
                )
                if r.acknowledged:
                    if r.modified_count != len(jids):
                        self.logger.error(
                            "Failed to update all running statuses: %d of %d",
                            r.modified_count,
                            len(jids),
                        )
                else:
                    self.logger.error("Failed to update running status")
                # Fetch contexts
                # version -> key -> job
                cjobs = {}
                for j in rjobs:
                    if not j.context_version:
                        continue
                    if j.context_version not in cjobs:
                        cjobs[j.context_version] = {}
                    cjobs[j.context_version][j.get_context_cache_key()] = j
                if cjobs:
                    for v in cjobs:
                        try:
                            ctx = self.get_cache().get_many(cjobs[v], version=v) or {}
                        except Exception as e:
                            self.logger.error("Failed to restore context: %s", e)
                            ctx = {}
                        for k in cjobs[v]:
                            cjobs[v][k].load_context(ctx.get(k, {}))
                #
                for job in rjobs:
                    if job.is_retries_exceeded():
                        metrics["%s_jobs_retries_exceeded" % self.name] += 1
                    in_label = None
                    if config.features.forensic:
                        in_label = "%s:%s" % (job.attrs[Job.ATTR_CLASS], job.attrs[Job.ATTR_KEY])
                    executor.submit(job.run, _in_label=in_label)
                    metrics["%s_jobs_started" % self.name] += 1
                    n += 1
            if jobs:
                # Wait for next job within check_interval
                njts = jobs[0].attrs[Job.ATTR_TS]
                now = datetime.datetime.now()
                if njts > now:
                    dt = njts - now
                    dt = (dt.microseconds + dt.seconds * 1000000.0) / 1000000.0
                    dt = max(dt, self.min_sleep)
                    time.sleep(dt)
        return n

    def apply_bulk_ops(self):
        if not self.bulk:
            return  # Nothing to apply
        t0 = perf_counter()
        with self.bulk_lock:
            try:
                r = self.collection.bulk_write(self.bulk)
                dt = perf_counter() - t0
                self.logger.info(
                    "%d bulk operations complete in %dms: " "inserted=%d, updated=%d, removed=%d",
                    len(self.bulk),
                    int(dt * 1000),
                    r.inserted_count,
                    r.modified_count,
                    r.deleted_count,
                )
            except pymongo.errors.BulkWriteError as e:
                self.logger.error("Cannot apply bulk operations: %s [%s]", e.details, e.code)
                metrics["%s_bulk_failed" % self.name] += 1
                return
            except Exception as e:
                self.logger.error("Cannot apply bulk operations: %s", e)
                metrics["%s_bulk_failed" % self.name] += 1
                return
            finally:
                self.bulk = []

    def remove_job(self, jcls, key=None):
        """
        Remove job from schedule
        """
        self.logger.info("Remove job %s(%s)", jcls, key)
        self.get_collection().delete_many({Job.ATTR_CLASS: jcls, Job.ATTR_KEY: key})

    def remove_job_by_id(self, jid):
        """
        Remove job from schedule
        """
        self.logger.info("Remove job: %s", jid)
        with self.bulk_lock:
            self.bulk.append(DeleteOne({Job.ATTR_ID: jid}))

    def postpone_job(self, jid: str) -> None:
        """
        Postpone job execution until next restart.
        """
        self.logger.info("Postpoing job until restart: %s", jid)
        with self.bulk_lock:
            self.bulk.append(UpdateOne({Job.ATTR_ID: jid}, {Job.ATTR_STATUS: Job.S_POSTPONED}))

    def submit(
        self,
        jcls,
        key=None,
        data=None,
        ts=None,
        delta=None,
        keep_ts=False,
        max_runs=None,
        shard=None,
    ):
        """
        Submit new job or adjust existing one
        :param jcls: Job class name
        :param key: Job key
        :param data: Job data (will be passed as handler's arguments)
        :param ts: Set next run time (datetime)
        :param delta: Set next run time after delta seconds
        :param keep_ts: Do not touch timestamp of existing jobs,
            set timestamp only for created jobs
        :param max_runs: Limit maximum runs attempts
        :param shard: Shard number for job
        """
        now = datetime.datetime.now()
        data = data or {}
        set_op = {}
        iset_op = {
            Job.ATTR_STATUS: Job.S_WAIT,
            Job.ATTR_RUNS: 0,
            Job.ATTR_FAULTS: 0,
            Job.ATTR_OFFSET: random.random(),
        }
        if max_runs is not None:
            iset_op[Job.ATTR_MAX_RUNS] = max_runs
        if ts:
            set_op[Job.ATTR_TS] = ts
        elif delta:
            set_op[Job.ATTR_TS] = now + datetime.timedelta(seconds=delta)
        else:
            set_op[Job.ATTR_TS] = now
        if keep_ts:
            iset_op[Job.ATTR_TS] = set_op.pop(Job.ATTR_TS)
        if data:
            set_op[Job.ATTR_DATA] = data
        if shard is not None:
            set_op[Job.ATTR_SHARD] = shard
        q = {Job.ATTR_CLASS: jcls, Job.ATTR_KEY: key}
        op = {"$setOnInsert": iset_op}
        if set_op:
            op["$set"] = set_op
        self.logger.info(
            "Submit job %s(%s, %s) at %s",
            jcls,
            key,
            data,
            set_op.get(Job.ATTR_TS) or iset_op.get(Job.ATTR_TS),
        )
        self.logger.debug("update(%s, %s, upsert=True)", q, op)
        self.get_collection().update_many(q, op, upsert=True)

    def set_next_run(
        self,
        jid,
        status=None,
        ts=None,
        delta=None,
        duration=None,
        context=None,
        context_version=None,
        context_key=None,
    ):
        """
        Reschedule job and set next run time
        :param jid: Job id
        :param status: Register run status
        :param ts: Set next run time (datetime)
        :param delta: Set next run time after delta seconds
        :param duration: Set last run duration (in seconds)
        :param context_version: Job context format version
        :param context: Stored job context
        :param context_key: Cache key for context
        """
        # Build increase/set operations
        now = datetime.datetime.now()
        set_op = {Job.ATTR_STATUS: Job.S_WAIT, Job.ATTR_LAST: now}
        inc_op = {}
        if status:
            set_op[Job.ATTR_LAST_STATUS] = status
        if ts:
            set_op[Job.ATTR_TS] = ts
        elif delta:
            set_op[Job.ATTR_TS] = now + datetime.timedelta(seconds=delta)
        else:
            set_op[Job.ATTR_TS] = now
        if duration:
            set_op[Job.ATTR_LAST_DURATION] = duration
        if status:
            inc_op[Job.ATTR_RUNS] = 1
            set_op[Job.ATTR_LAST_STATUS] = status
            if status == Job.E_SUCCESS:
                set_op[Job.ATTR_LAST_SUCCESS] = now
                set_op[Job.ATTR_FAULTS] = 0
            elif status == Job.E_EXCEPTION:
                inc_op[Job.ATTR_FAULTS] = 1
        if context_version is not None:
            self.cache_set(key=context_key, value=context, version=context_version)
        op = {}
        if set_op:
            op["$set"] = set_op
        if inc_op:
            op["$inc"] = inc_op

        if op:
            q = {Job.ATTR_ID: jid, Job.ATTR_STATUS: {"$ne": Job.S_SUSPEND}}
            self.logger.debug("update(%s, %s)", q, op)
            with self.bulk_lock:
                self.bulk += [UpdateOne(q, op)]

    def apply_cache_ops(self):
        with self.cache_lock:
            cache_set_ops = self.cache_set_ops
            self.cache_set_ops = {}
        if not cache_set_ops:
            return
        cache = self.get_cache()
        for version in cache_set_ops:
            metrics["%s_cache_set_requests" % self.name] += 1
            try:
                cache.set_many(cache_set_ops[version], version=version, ttl=self.CACHE_DEFAULT_TTL)
            except Exception as e:
                self.logger.error("Error writing cache: %s", e)
                metrics["%s_cache_set_errors" % self.name] += 1

    def cache_set(self, key, value, version):
        with self.cache_lock:
            if version not in self.cache_set_ops:
                self.cache_set_ops[version] = {}
            self.cache_set_ops[version][key] = value

    def apply_metrics(self, d):
        """
        Append scheduler metrics to dictionary d
        :param d:
        :return:
        """
        if self.executor:
            self.executor.apply_metrics(d)
        d.update({"%s_jobs_burst" % self.name: len(self.jobs_burst)})

    def shutdown(self, sync=False):
        self.to_shutdown = True
        if self.executor:
            f = self.executor.shutdown(sync)
        else:
            f = asyncio.Future()
            f.set_result(True)
        f.add_done_callback(lambda _: self.apply_ops())
        return f
