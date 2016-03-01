# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Scheduler Job Class
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import datetime
import random
## Third-party modules
import pymongo.errors
import tornado.gen
import tornado.ioloop
from concurrent.futures import ThreadPoolExecutor
## NOC modules
from job import Job
from noc.lib.nosql import get_db
from noc.lib.solutions import get_solution


class Scheduler(object):
    COLLECTION_BASE = "noc.schedules."

    SUBMIT_THRESHOLD_FACTOR = 10
    MAX_CHUNK_FACTOR = 4

    def __init__(self, name, pool=None, reset_running=False,
                 max_threads=5, ioloop=None, check_time=1000,
                 submit_threshold=None, max_chunk=None):
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

    def run(self):
        """
        Run scheduler. Common usage

        scheduler.run(ioloop=ioloop)
        ioloop.run()
        """
        if self.reset_running:
            self.reset_running()
        self.ensure_indexes()
        self.logger.info("Running scheduler")
        self.run_callback = tornado.ioloop.PeriodicCallback(
            self.run_pending,
            self.check_time,
            self.ioloop
        )
        self.run_callback.start()

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
        r = self.get_collection().update({
            Job.ATTR_STATUS: Job.S_RUN
        }, {
            "$set": {
                Job.ATTR_STATUS: Job.S_WAIT
            }
        }, multi=True, safe=True)
        nm = r.get("nModified", 0)
        if nm:
            self.logger.debug("Resetted: %d", nm)
        else:
            self.logger.debug("Nothing to reset")

    def ensure_indexes(self):
        """
        Create all nesessary indexes
        """
        self.logger.debug("Check indexes")
        self.get_collection().ensure_index([("ts", 1)])
        self.get_collection().ensure_index([("jcls", 1), ("key", 1)])
        self.logger.debug("Indexes are ready")

    def iter_pending_jobs(self, limit):
        """
        Yields pending jobs
        """
        qs = self.get_collection().find({
            Job.ATTR_TS: {
                "$lte": datetime.datetime.now(),
            },
            Job.ATTR_STATUS: Job.S_WAIT
        }).limit(limit).sort(Job.ATTR_TS)
        try:
            for job in qs:
                yield job
        except pymongo.errors.CursorNotFound:
            self.logger.info("Server cursor timed out. Waiting for next cycle")
        except pymongo.errors.OperationFailure, why:
            self.logger.error("Operation failure: %s", why)
            self.logger.error("Trying to recover")

    @tornado.gen.coroutine
    def run_pending(self):
        """
        Read and launch all pending jobs
        """
        executor = self.get_executor()
        collection = self.get_collection()
        n = 0
        # Check we can submit new jobs
        while executor._work_queue.qsize() < self.submit_threshold:
            jobs = []
            jids = []
            n = 0
            for job_data in self.iter_pending_jobs(self.max_chunk):
                try:
                    jcls = get_solution(job_data[Job.ATTR_CLASS])
                except ImportError, why:
                    self.logger.error("Invalid job class %s",
                                      job_data[Job.ATTR_CLASS])
                    self.logger.error("Error: %s", why)
                    self.remove_job(
                        job_data[Job.ATTR_CLASS],
                        job_data[Job.ATTR_KEY]
                    )
                    continue
                jobs += [jcls(self, job_data)]
                jids += [job_data["_id"]]
                n += 1
            if not n:
                break  # No pending data
            if jobs:
                self.logger.debug(
                    "update({_id: {$in: %s}}, {$set: {%s: '%s'}})",
                    jids, Job.ATTR_STATUS, Job.S_RUN
                )
                collection.update({
                    "_id": {
                        "$in": jids
                    }
                }, {
                    "$set": {
                        Job.ATTR_STATUS: Job.S_RUN
                    }
                }, multi=True, safe=True)
                for job in jobs:
                    executor.submit(job.run)
        if n:
            self.logger.info("All workers are busy. Waiting")

    def remove_job(self, jcls, key=None):
        """
        Remove job from schedule
        """
        self.logger.info("Remove job %s(%s)", jcls, key)
        self.get_collection().remove({
            Job.ATTR_CLASS: jcls,
            Job.ATTR_KEY: key
        })

    def submit(self, jcls, key=None, data=None, ts=None, delta=None):
        """
        Submit new job or adjust existing one
        :param jcls: Job class name
        :param key: Job key
        :param data: Job data (will be passed as handler's arguments)
        :param ts: Set next run time (datetime)
        :param delta: Set next run time after delta seconds
        """
        now = datetime.datetime.now()
        data = data or {}
        set_op = {}
        if ts:
            set_op[Job.ATTR_TS] = ts
        elif delta:
            set_op[Job.ATTR_TS] = (now +
                                   datetime.timedelta(seconds=delta))
        else:
            set_op[Job.ATTR_TS] = now
        if data:
            set_op[Job.ATTR_DATA] = data
        q = {
            Job.ATTR_CLASS: jcls,
            Job.ATTR_KEY: key
        }
        op = {
            "$set": set_op,
            "$setOnInsert": {
                Job.ATTR_STATUS: Job.S_WAIT,
                Job.ATTR_RUNS: 0,
                Job.ATTR_FAULTS: 0,
                Job.ATTR_OFFSET: random.random()
            }
        }
        self.logger.info("Submit job %s(%s, %s) at %s",
                         jcls, key, data, set_op[Job.ATTR_TS])
        self.logger.debug("update(%s, %s, upsert=True)", q, op)
        self.get_collection().update(q, op, upsert=True)

    def set_next_run(self, jcls, key, status=None, ts=None, delta=None,
                     duration=None):
        """
        Reschedule job and set next run time
        :param jcls: Job class name
        :param key: Job key
        :param status: Register run status
        :param ts: Set next run time (datetime)
        :param delta: Set next run time after delta seconds
        :param duration: Set last run duration (in seconds)
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
            set_op[Job.ATTR_TS] = (now +
                                    datetime.timedelta(seconds=delta))
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

        op = {}
        if set_op:
            op["$set"] = set_op
        if inc_op:
            op["$inc"] = inc_op

        if op:
            q = {
                Job.ATTR_CLASS: jcls,
                Job.ATTR_KEY: key
            }
            self.logger.debug("update(%s, %s)", q, op)
            self.get_collection().update(q, op)
