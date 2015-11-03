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

    def __init__(self, name, pool=None, reset_running=False,
                 max_threads=5, ioloop=None):
        """
        Create scheduler
        :param name: Unique scheduler name
        :param pool: Pool name, if run in pooled mode
        :param reset_running: Reset all running jobs to
            wait state on start
        :param max_threads: Thread executor threads
        :param ioloop: IOLoop instance
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
            1000,  # 1s
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
        self.logger.debug("Resetted: %d", r["nModified"])

    def ensure_indexes(self):
        """
        Create all nesessary indexes
        """
        self.logger.debug("Check indexes")
        self.get_collection().ensure_index([("ts", 1)])
        self.get_collection().ensure_index([("jcls", 1), ("key", 1)])
        self.logger.debug("Indexes are ready")

    def iter_pending_jobs(self):
        """
        Yields pending jobs
        """
        qs = self.get_collection().find({
            Job.ATTR_TS: {
                "$lte": datetime.datetime.now(),
            },
            Job.ATTR_STATUS: Job.S_WAIT
        }).sort(Job.ATTR_TS)
        try:
            for job in qs.batch_size(100):
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
        for job_data in self.iter_pending_jobs():
            try:
                jcls = get_solution(job_data[Job.ATTR_CLASS])
            except ImportError:
                self.logger.error("Invalid job class %s",
                                  job_data[Job.ATTR_CLASS])
                self.remove_job(
                    job_data[Job.ATTR_CLASS],
                    job_data[Job.ATTR_KEY]
                )
                continue
            # @todo: Group restrictions
            job = jcls(self, job_data)
            self.logger.debug(
                "update({_id: %s}, {$set: {%s: '%s'}})",
                job_data["_id"], Job.ATTR_STATUS, Job.S_RUN
            )
            self.get_collection().update({
                "_id": job_data["_id"]
            }, {
                "$set": {
                    Job.ATTR_STATUS: Job.S_RUN
                }
            })
            self.get_executor().submit(job.run)

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
                Job.ATTR_OFFSET: random.random(),
                Job.ATTR_DATA: data
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
            Job.ATTR_STATUS: Job.S_WAIT
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
