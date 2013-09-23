# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Scheduler Job Class
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import logging
import time
import datetime
import inspect
import threading
from collections import defaultdict
## NOC modules
from error import JobExists
from job import Job
from noc.lib.nosql import get_db
from noc.lib.debug import error_report, get_traceback


class Scheduler(object):
    COLLECTION_BASE = "noc.schedules."
    ATTR_TS = "ts"
    ATTR_CLASS = "jcls"
    ATTR_STATUS = "s"
    ATTR_TIMEOUT = "timeout"
    ATTR_KEY = "key"
    ATTR_DATA = "data"
    ATTR_SCHEDULE = "schedule"
    ATTR_LAST = "last"  # last run
    ATTR_LAST_STATUS = "ls"  # last completion status
    ATTR_LAST_DURATION = "ldur"  # last job duration
    ATTR_RUNS = "runs"  # Number of runs
    ATTR_TRACEBACK = "tb"  # Last error traceback
    ATTR_LOG = "log"  # Job log
    S_WAIT = "W"  # Waiting to run
    S_RUN = "R"   # Running
    S_STOP = "S"  # Stopped by operator
    S_FAIL = "F"  # Not used yet

    JobExists = JobExists

    def __init__(self, name, cleanup=None, reset_running=False,
                 initial_submit=False, max_threads=None,
                 preserve_order=False):
        self.name = name
        self.job_classes = {}
        self.collection_name = self.COLLECTION_BASE + self.name
        self.collection = get_db()[self.collection_name]
        self.active_mrt = {}  # ReduceTask -> Job instance
        self.cleanup_callback = cleanup
        self.reset_running = reset_running
        self.ignored = []
        self.initial_submit = initial_submit
        self.initial_submit_next_check = {}  # job class -> timestamp
        self.max_threads = max_threads
        self.preserve_order = preserve_order
        self.running_lock = threading.Lock()
        self.running_count = defaultdict(int)  # Group -> Count

    def ensure_indexes(self):
        if self.preserve_order:
            k = [("ts", 1), ("_id", 1)]
        else:
            k = [("ts", 1)]
        self.debug("Checking indexes: %s" % ", ".join(x[0] for x in k))
        self.collection.ensure_index(k)
        self.debug("Indexes are ready")

    def debug(self, msg):
        logging.debug("[%s] %s" % (self.name, msg))

    def info(self, msg):
        logging.info("[%s] %s" % (self.name, msg))

    def error(self, msg):
        logging.error("[%s] %s" % (self.name, msg))

    def register_job_class(self, cls):
        if not cls.name:
            return  # Abstract classes
        s = " (ignored)" if cls.ignored else ""
        self.info("Registering job class: %s%s" % (cls.name, s))
        self.job_classes[cls.name] = cls
        # Set up ignored jobs
        if cls.ignored:
            self.ignored += [cls.name]
        else:
            # Initialize job class
            cls.initialize(self)
            # Register intial submit handlers
            if (self.initial_submit and
                hasattr(cls, "initial_submit") and
                callable(cls.initial_submit) and
                hasattr(cls, "initial_submit_interval")):
                self.initial_submit_next_check[cls] = time.time()

    def register_all(self, path, exclude=None):
        """
        Register all Job classes defined within directory
        :param path:
        :return:
        """
        exclude = exclude or []
        if not os.path.isdir(path):
            raise ValueError("'%s' must be a directory" % path)
        mr = "noc.%s." % ".".join(path.split(os.sep))
        for f in os.listdir(path):
            if f in exclude or not f.endswith(".py"):
                continue
            mn = mr + f[:-3]  # Full module name
            m = __import__(mn, {}, {}, "*")
            for on in dir(m):
                o = getattr(m, on)
                if (inspect.isclass(o) and issubclass(o, Job) and
                    o.__module__.startswith(mn)):
                    self.register_job_class(o)

    def get_job_class(self, name):
        return self.job_classes[name]

    def submit(self, job_name, key=None, data=None,
               schedule=None, ts=None):
        """
        Submit new job
        """
        if ts is None:
            ts = datetime.datetime.now()
        elif type(ts) in (int, long, float):
            ts = (datetime.datetime.now() +
                  datetime.timedelta(seconds=ts))
        # Check Job is not exists
        if key is not None:
            if self.collection.find_one({
                self.ATTR_CLASS: job_name,
                self.ATTR_KEY: key
            }):
                raise JobExists()
        # Submit job
        id = self.collection.insert({
            self.ATTR_TS: ts,
            self.ATTR_CLASS: job_name,
            self.ATTR_STATUS: self.S_WAIT,
            self.ATTR_KEY: key,
            self.ATTR_DATA: data,
            self.ATTR_SCHEDULE: schedule
        }, manipulate=True, safe=True)
        self.info("Scheduling job %s(%s) id=%s at %s" % (
            job_name, key, id, ts))

    def remove_job(self, job_name, key):
        self.info("Removing job %s(%s)" % (job_name, key))
        self.collection.remove({
            self.ATTR_CLASS: job_name,
            self.ATTR_KEY: key
        }, safe=True)

    def reschedule_job(self, job_name, key, ts, status=None,
                       duration=None, last_status=None, tb=None,
                       log=None, update_runs=False,
                       skip_running=False):
        self.info("Rescheduling job %s(%s) to %s%s" % (
            job_name, key, ts, " status=%s" % status if status else ""))
        q = {
            self.ATTR_CLASS: job_name,
            self.ATTR_KEY: key
        }
        if skip_running:
            q[self.ATTR_STATUS] = self.S_WAIT
        s = {
            self.ATTR_TS: ts,
            self.ATTR_TRACEBACK: tb,
            self.ATTR_LOG: log or []
        }
        if status:
            s[self.ATTR_STATUS] = status
        if last_status:
            s[self.ATTR_LAST_STATUS] = last_status
        if duration is not None:
            s[self.ATTR_LAST_DURATION] = duration
        op = {"$set": s}
        if update_runs:
            op["$inc"] = {self.ATTR_RUNS: 1}
        self.collection.update(q, op, safe=True)

    def set_job_status(self, job_name, key, status):
        self.info("Changing %s(%s) status to %s" % (
            job_name, key, status))
        self.collection.update({
            self.ATTR_CLASS: job_name,
            self.ATTR_KEY: key
        }, {
            "$set": {self.ATTR_STATUS: status}
        }, safe=True)

    def run_job(self, job):
        """
        Begin job execution
        :param job:
        :return:
        """
        # Dereference job
        if not job.dereference():
            logging.info("Cannot dereference job %s(%s). Removing" % (
                job.name, job.key))
            self.remove_job(job.name, job.key)
            return
        # Check threaded jobs limit
        if job.threaded and self.max_threads:
            if threading.active_count() >= self.max_threads:
                return
        # Check job can be run
        if not job.can_run():
            self._complete_job(job, job.S_DEFERRED, None)
            return
        # Change status
        s = "threaded " if job.threaded else ""
        self.info("Running %sjob %s(%s)" % (s, job.name, job.get_display_key()))
        job.started = time.time()
        self.collection.update({
            self.ATTR_CLASS: job.name,
            self.ATTR_KEY: job.key
        }, {"$set": {
            self.ATTR_STATUS: self.S_RUN,
            self.ATTR_LAST: datetime.datetime.fromtimestamp(job.started)
        }})
        #
        if job.map_task:
            # Run in MRT mode
            t = ReduceTask.create_task(
                job.get_managed_object(),  # Managed object is in key
                None, {},
                job.map_task, job.get_map_task_params()
            )
            self.active_mrt[t] = job
        else:
            self._run_job_handler(job)

    def _run_job_handler(self, job, **kwargs):
        if job.threaded:
            t = threading.Thread(target=self._job_wrapper,
                args=(job,), kwargs=kwargs
            )
            t.daemon = True
            t.start()
        else:
            return self._job_wrapper(job, **kwargs)

    def _job_wrapper(self, job, **kwargs):
        tb = None
        try:
            r = job.handler(**kwargs)
        except Exception:
            error_report()
            job.on_exception()
            s = job.S_EXCEPTION
            tb = get_traceback()
        else:
            if r:
                self.info("Job %s(%s) is completed successfully" % (
                    job.name, job.get_display_key()))
                job.on_success()
                s = job.S_SUCCESS
            else:
                self.info("Job %s(%s) is failed" % (
                    job.name, job.get_display_key()))
                job.on_failure()
                s = job.S_FAILED
        self._complete_job(job, s, tb)

    def _complete_job(self, job, status, tb):
        group = job.get_group()
        if group is not None:
            with self.running_lock:
                self.running_count[group] -= 1
                if not self.running_count[group]:
                    del self.running_count[group]
        on_complete = job.on_complete
        t = job.get_schedule(status)
        if t is None:
            # Unschedule job
            self.remove_job(job.name, job.key)
        else:
            # Reschedule job
            t1 = time.time()
            self.reschedule_job(
                job.name, job.key, t,
                status="W",
                last_status=status,
                duration=t1 - job.started,  # @todo: maybe error
                tb=tb,
                update_runs=True
            )
        # Reschedule jobs must be executed on complete
        for job_name, key in on_complete:
            ts = datetime.datetime.now()
            self.reschedule_job(job_name, key, ts, skip_running=True)

    def complete_mrt_job(self, t):
        job = self.active_mrt.pop(t)
        for m in t.maptask_set.all():
            if m.status == "C":
                self._run_job_handler(job, object=m.managed_object,
                    result=m.script_result)
            else:
                self.info("Job %s(%s) is failed" % (
                    job.name, job.get_display_key()))
                self._complete_job(job, self.S_FAIL, m.script_result)
        t.delete()

    def run_pending(self):
        n = 0
        # Run pending intial submits
        if self.initial_submit_next_check:
            for jcls in self.initial_submit_next_check:
                if jcls.name in self.ignored:
                    continue
                t0 = time.time()
                if self.initial_submit_next_check[jcls] <= t0:
                    # Get existing keys
                    keys = [x[self.ATTR_KEY] for x in
                            self.collection.find({
                                self.ATTR_CLASS: jcls.name
                            }, [self.ATTR_KEY])]
                    # Run initial submit
                    try:
                        self.info("Running initial submit for %s" % jcls.name)
                        jcls.initial_submit(self, keys)
                    except Exception:
                        error_report()
                    # Reschedule initial submit
                    self.initial_submit_next_check[jcls] = (
                        t0 + jcls.initial_submit_interval)
        # Check for complete MRT
        if self.active_mrt:
            complete = [t for t in self.active_mrt if t.complete]
            for t in complete:
                self.complete_mrt_job(t)
            self.active_mrt = dict(
                (t, self.active_mrt[t])
                    for t in self.active_mrt if t not in complete)
        # Check for pending persistent tasks
        q = {
            self.ATTR_TS: {"$lte": datetime.datetime.now()},
            self.ATTR_STATUS: self.S_WAIT
        }
        if self.ignored:
            q[self.ATTR_CLASS] = {"$nin": self.ignored}
        # Get remaining pending tasks
        qs = self.collection.find(q)
        if self.preserve_order:
            qs = qs.sort([(self.ATTR_TS, 1), ("_id", 1)])
        else:
            qs = qs.sort(self.ATTR_TS)
        for job_data in qs:
            jcls = self.job_classes.get(job_data[self.ATTR_CLASS])
            if not jcls:
                # Invalid job class. Park job to FAIL state
                self.error("Invalid job class: %s" % jcls)
                self.set_job_status(job_data[self.ATTR_CLASS],
                    job_data[self.ATTR_KEY], self.S_FAIL)
                continue
            job = jcls(self,
                job_data[self.ATTR_KEY], job_data[self.ATTR_DATA],
                job_data[self.ATTR_SCHEDULE]
            )
            # Check for late jobs
            if (job.max_delay and
                job_data[self.ATTR_TS] < datetime.datetime.now() - datetime.timedelta(seconds=job.max_delay)):
                self.info("Job %s(%s) is scheduled too late" % (
                    job.name, job.get_display_key()))
                job.started = time.time()
                self._complete_job(job, job.S_LATE, None)
                continue
            # Check for group limits
            group = job.get_group()
            if self.can_run(job):
                if group is not None:
                    with self.running_lock:
                        self.running_count[group] += 1
                self.run_job(job)
                n += 1
        return n

    def run(self):
        if self.reset_running:
            # Change running to waiting
            self.debug("Resetting running jobs")
            self.collection.update({
                self.ATTR_STATUS: self.S_RUN
            }, {
                "$set": {self.ATTR_STATUS: self.S_WAIT}
            }, multi=True, safe=True)
        self.ensure_indexes()
        self.info("Running scheduler")
        while True:
            if not self.run_pending():
                time.sleep(1)
            else:
                self.cleanup()

    def wipe(self):
        """
        Wipe off all schedules
        """
        self.collection.drop()

    def cleanup(self):
        if self.cleanup_callback:
            self.cleanup_callback()

    def get_running_count(self):
        with self.running_lock:
            return self.running_count.copy()

    def can_run(self, job):
        return True

    def get_job(self, job_class, key=None):
        return self.collection.find_one({
            self.ATTR_CLASS: job_class,
            self.ATTR_KEY: key
        })


## Avoid circular reference
from noc.sa.models.reducetask import ReduceTask
