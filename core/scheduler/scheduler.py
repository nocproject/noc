# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Scheduler Job Class
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import datetime
import random
import Queue
import threading
## Third-party modules
import pymongo.errors
import tornado.gen
import tornado.ioloop
from concurrent.futures import ThreadPoolExecutor
## NOC modules
from job import Job
from noc.lib.nosql import get_db
from noc.core.handler import get_handler


class Scheduler(object):
    COLLECTION_BASE = "noc.schedules."

    SUBMIT_THRESHOLD_FACTOR = 10
    MAX_CHUNK_FACTOR = 1
    UPDATES_PER_CHECK = 4

    def __init__(self, name, pool=None, reset_running=False,
                 max_threads=5, ioloop=None, check_time=1000,
                 submit_threshold=None, max_chunk=None,
                 filter=None, use_cache=None):
        """
        Create scheduler
        :param name: Unique scheduler name
        :param pool: Pool name, if run in pooled mode
        :param reset_running: Reset all running jobs to
            wait state on start
        :param max_threads: Thread executor threads
        :param ioloop: IOLoop instance
        :param check_time: time in milliseconds to check for new jobs
        :param max_chunk: Maximum amount of jobs which can be submitted
            at one step
        :param submit_threshold: Maximal executor queue length
            when submitting of next chunk is allowed
        :param filter: Additional filter to be applied to
            pending jobs
        """
        self.logger = logging.getLogger("scheduler.%s" % name)
        self.name = name
        self.collection_name = self.COLLECTION_BASE + self.name
        self.pool = pool
        if pool:
            self.collection_name += ".%s" % pool
        self.ioloop = ioloop or tornado.ioloop.IOLoop.current()
        self.to_reset_running = reset_running
        self.running_groups = set()
        self.collection = None
        self.max_threads = max_threads
        self.executor = None
        self.run_callback = None
        self.check_time = check_time
        self.read_ahead_interval = datetime.timedelta(milliseconds=check_time)
        if submit_threshold:
            self.submit_threshold = submit_threshold
        else:
            self.submit_threshold = max(
                self.max_threads // self.SUBMIT_THRESHOLD_FACTOR,
                1
            )
        if max_chunk:
            self.max_chunk = max_chunk
        else:
            self.max_chunk = max(
                self.max_threads // self.MAX_CHUNK_FACTOR,
                2
            )
        self.filter = filter
        self.to_shutdown = False
        self.min_sleep = float(check_time) / self.UPDATES_PER_CHECK / 1000.0
        self.jobs_burst = []
        self.use_cache = use_cache
        self.cache = None
        self.cache_thread = None
        self.cache_queue = Queue.Queue()

    def run(self):
        """
        Run scheduler. Common usage

        scheduler.run(ioloop=ioloop)
        ioloop.run()
        """
        if self.to_reset_running:
            self.reset_running()
        self.ensure_indexes()
        if self.use_cache:
            self.run_cache_thread()
        self.logger.info("Running scheduler")
        self.ioloop.spawn_callback(self.scheduler_loop)

    def run_cache_thread(self):
        from noc.core.cache.base import cache
        self.cache = cache
        self.cache_thread = threading.Thread(
            target=self.cache_worker,
            name="cache_worker"
        )
        self.cache_thread.setDaemon(True)
        self.cache_thread.start()

    def get_collection(self):
        """
        Returns mongo collection instance
        """
        if not self.collection:
            self.logger.debug("Open collection %s",
                              self.collection_name)
            self.collection = get_db()[self.collection_name]
        return self.collection

    def get_executor(self):
        """
        Returns threadpool executor
        """
        if not self.executor:
            self.logger.debug("Run thread executor (%d threads)",
                              self.max_threads)
            self.executor = ThreadPoolExecutor(self.max_threads)
        return self.executor

    def reset_running(self):
        """
        Reset all running jobs to waiting status
        """
        self.logger.debug("Reset running jobs")
        r = self.get_collection().update(self.get_query({
            Job.ATTR_STATUS: Job.S_RUN
        }), {
            "$set": {
                Job.ATTR_STATUS: Job.S_WAIT
            }
        }, multi=True, safe=True)
        if r["ok"]:
            nm = r.get("nModified", 0)
            if nm:
                self.logger.info("Reset: %d", nm)
            else:
                self.logger.info("Nothing to reset")
        else:
            self.logger.info("Failed to reset running jobs")

    def ensure_indexes(self):
        """
        Create all nesessary indexes
        """
        self.logger.debug("Check indexes")
        self.get_collection().ensure_index(
            [("ts", 1)],
            partialFilterExpression={"s": "W"}
        )
        self.get_collection().ensure_index([("jcls", 1), ("key", 1)])
        self.logger.debug("Indexes are ready")

    def get_query(self, q):
        """
        Combine filter with query and return resulting query
        """
        if self.filter:
            qq = self.filter.copy()
            qq.update(q)
            return qq
        else:
            return q

    @tornado.gen.coroutine
    def scheduler_loop(self):
        """
        Primary scheduler loop
        """
        while not self.to_shutdown:
            t0 = self.ioloop.time()
            try:
                n = yield self.run_pending()
            except Exception as e:
                self.logger.error("Failed to schedule next tasks: %s", e)
                n = 0
            dt = self.check_time - (self.ioloop.time() - t0) * 1000
            if dt > 0:
                if n:
                    dt = min(dt, self.check_time / n)
                yield tornado.gen.sleep(dt / 1000.0)

    def iter_pending_jobs(self, limit):
        """
        Yields pending jobs
        """
        qs = self.get_collection().find(self.get_query({
            Job.ATTR_TS: {
                "$lte": datetime.datetime.now() + self.read_ahead_interval
            },
            Job.ATTR_STATUS: Job.S_WAIT
        })).limit(limit).sort(Job.ATTR_TS)
        try:
            for job in qs:
                try:
                    jcls = get_handler(job[Job.ATTR_CLASS])
                    yield jcls(self, job)
                except ImportError as e:
                    self.logger.error("Invalid job class %s",
                                      job[Job.ATTR_CLASS])
                    self.logger.error("Error: %s", e)
                    self.remove_job_by_id(job[Job.ATTR_ID])
        except pymongo.errors.CursorNotFound:
            self.logger.info("Server cursor timed out. Waiting for next cycle")
        except pymongo.errors.OperationFailure as e:
            self.logger.error("Operation failure: %s", e)
            self.logger.error("Trying to recover")
        except pymongo.errors.AutoReconnect:
            self.logger.error("Auto-reconnect detected. Waiting for next cycle")

    @tornado.gen.coroutine
    def run_pending(self):
        """
        Read and launch all pending jobs
        """
        executor = self.get_executor()
        collection = self.get_collection()
        n = 0
        if self.submit_threshold <= executor._work_queue.qsize():
            raise tornado.gen.Return(n)
        jobs, self.jobs_burst = self.jobs_burst, []
        burst_ids = set(j.attrs[Job.ATTR_ID] for j in jobs)
        if len(jobs) <= self.max_chunk // 2:
            jobs += [
                j for j in self.iter_pending_jobs(self.max_chunk)
                if j.attrs[Job.ATTR_ID] not in burst_ids
            ]
        while jobs:
            may_submit = max(
                self.submit_threshold - executor._work_queue.qsize(),
                0
            )
            if not may_submit:
                self.logger.info("All workers are busy. Sending %d jobs to burst", len(jobs))
                self.jobs_burst = jobs
                break
            now = datetime.datetime.now()
            rl = min(
                sum(1 for j in jobs if j.attrs[Job.ATTR_TS] <= now),
                may_submit
            )
            rjobs, jobs = jobs[:rl], jobs[rl:]
            if rjobs:
                jids = [j.attrs[Job.ATTR_ID] for j in rjobs]
                self.logger.debug(
                    "update({_id: {$in: %s}}, {$set: {%s: '%s'}})",
                    jids, Job.ATTR_STATUS, Job.S_RUN
                )
                r = collection.update({
                    "_id": {
                        "$in": jids
                    }
                }, {
                    "$set": {
                        Job.ATTR_STATUS: Job.S_RUN
                    }
                }, multi=True, safe=True)
                if not r["ok"]:
                    self.logger.error("Failed to update running status")
                if r["nModified"] != len(jids):
                    self.logger.error(
                        "Failed to update all running statuses: %d of %d",
                        r["nModified"], len(jids)
                    )
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
                            ctx = self.cache.get_many(cjobs[v], version=v) or {}
                        except Exception as e:
                            self.logger.error("Failed to restore context: %s", e)
                            ctx = {}
                        for k in cjobs[v]:
                            cjobs[v][k].load_context(ctx.get(k, {}))
                #
                for job in rjobs:
                    executor.submit(job.run)
                    n += 1
            if jobs:
                # Wait for next job within check_interval
                njts = jobs[0].attrs[Job.ATTR_TS]
                now = datetime.datetime.now()
                if njts > now:
                    dt = njts - now
                    dt = (dt.microseconds + dt.seconds * 1000000.0) / 1000000.0
                    dt = max(dt, self.min_sleep)
                    yield tornado.gen.sleep(dt)
        raise tornado.gen.Return(n)

    def remove_job(self, jcls, key=None):
        """
        Remove job from schedule
        """
        self.logger.info("Remove job %s(%s)", jcls, key)
        self.get_collection().remove({
            Job.ATTR_CLASS: jcls,
            Job.ATTR_KEY: key
        })

    def remove_job_by_id(self, jid):
        """
        Remove job from schedule
        """
        self.logger.info("Remove job %s", jid)
        self.get_collection().remove({
            Job.ATTR_ID: jid
        })

    def submit(self, jcls, key=None, data=None, ts=None, delta=None,
               keep_ts=False):
        """
        Submit new job or adjust existing one
        :param jcls: Job class name
        :param key: Job key
        :param data: Job data (will be passed as handler's arguments)
        :param ts: Set next run time (datetime)
        :param delta: Set next run time after delta seconds
        :param keep_ts: Do not touch timestamp of existing jobs,
            set timestamp only for created jobs
        """
        now = datetime.datetime.now()
        data = data or {}
        set_op = {}
        iset_op = {
            Job.ATTR_STATUS: Job.S_WAIT,
            Job.ATTR_RUNS: 0,
            Job.ATTR_FAULTS: 0,
            Job.ATTR_OFFSET: random.random()
        }
        if ts:
            set_op[Job.ATTR_TS] = ts
        elif delta:
            set_op[Job.ATTR_TS] = (now +
                                   datetime.timedelta(seconds=delta))
        else:
            set_op[Job.ATTR_TS] = now
        if keep_ts:
            iset_op[Job.ATTR_TS] = set_op.pop(Job.ATTR_TS)
        if data:
            set_op[Job.ATTR_DATA] = data
        q = {
            Job.ATTR_CLASS: jcls,
            Job.ATTR_KEY: key
        }
        op = {
            "$setOnInsert": iset_op
        }
        if set_op:
            op["$set"] = set_op
        self.logger.info(
            "Submit job %s(%s, %s) at %s",
            jcls, key, data,
            set_op.get(Job.ATTR_TS) or iset_op.get(Job.ATTR_TS))
        self.logger.debug("update(%s, %s, upsert=True)", q, op)
        self.get_collection().update(q, op, upsert=True)

    def set_next_run(self, jid, status=None, ts=None, delta=None,
                     duration=None,
                     context=None, context_version=None,
                     context_key=None):
        """
        Reschedule job and set next run time
        :param jid: Job id
        :param status: Register run status
        :param ts: Set next run time (datetime)
        :param delta: Set next run time after delta seconds
        :param duration: Set last run duration (in seconds)
        :param context_version: Job context format vresion
        :param context: Stored job context
        """
        # Build increase/set operations
        now = datetime.datetime.now()
        set_op = {
            Job.ATTR_STATUS: Job.S_WAIT,
            Job.ATTR_LAST: now
        }
        inc_op = {}
        if status:
            set_op[Job.ATTR_LAST_STATUS] = status
        if ts:
            set_op[Job.ATTR_TS] = ts
        elif delta:
            set_op[Job.ATTR_TS] = (now + datetime.timedelta(seconds=delta))
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
            self.cache_set(
                key=context_key,
                value=context,
                version=context_version
            )
        op = {}
        if set_op:
            op["$set"] = set_op
        if inc_op:
            op["$inc"] = inc_op

        if op:
            q = {
                Job.ATTR_ID: jid
            }
            self.logger.debug("update(%s, %s)", q, op)
            r = self.get_collection().update(q, op)
            if not r["ok"] or r["nModified"] != 1:
                self.logger.error("Failed to set next run for job %s", jid)

    def cache_worker(self):
        self.logger.info("Starting cache worker thread")
        set_ops = {}  # version -> key -> value
        SEND_INTERVAL = 0.25
        DEFAULT_TTL = 7 * 24 * 3600
        last = 0
        while True:
            t0 = self.ioloop.time()
            timeout = min(last + SEND_INTERVAL - t0, SEND_INTERVAL)
            if timeout > 0:
                # Collect operations
                try:
                    key, value, version = self.cache_queue.get(
                        block=True, timeout=timeout
                    )
                    if version not in set_ops:
                        set_ops[version] = {}
                    set_ops[version][key] = value
                except Queue.Empty:
                    pass
            else:
                # Apply operations
                if set_ops:
                    for version, data in set_ops.items():
                        try:
                            self.cache.set_many(
                                data, version=version,
                                ttl=DEFAULT_TTL)
                            del set_ops[version]
                        except Exception as e:
                            self.logger.error("Error writing cache: %s", e)
                last = t0

    def cache_set(self, key, value, version):
        assert self.cache_thread, "Cache management thread is not started"
        self.cache_queue.put(
            (key, value, version)
        )
