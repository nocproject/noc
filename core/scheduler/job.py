# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Scheduler Job Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import logging
import time
import datetime
# Third-party modules
import tornado.gen
# NOC modules
from noc.core.log import PrefixLoggerAdapter
from noc.core.debug import error_report
from noc.lib.dateutils import total_seconds

logger = logging.getLogger(__name__)


class Job(object):
    # Unique job name
    name = None
    # Set to False when job is disabled
    enabled = True
    # Model/Document class referenced by key
    model = None
    # Use model.get_by_id for dereference
    use_get_by_id = False
    # Group name. Only one job from group can be started
    # if is not None
    group_name = None
    # Context format version
    # None - do not store context
    # Set to version number otherwise
    # Bump to next number on incompatible context changes
    context_version = None
    #
    context_cache_key = "jobctx-%(name)s-%(pool)s-%(job_id)s"
    # Collection attributes
    ATTR_ID = "_id"
    ATTR_TS = "ts"
    ATTR_CLASS = "jcls"
    ATTR_STATUS = "s"
    ATTR_TIMEOUT = "timeout"
    ATTR_KEY = "key"
    ATTR_DATA = "data"
    ATTR_LAST = "last"  # timestamp of last run
    ATTR_LAST_STATUS = "ls"  # last completion status
    ATTR_LAST_DURATION = "ldur"  # last job duration, in success
    ATTR_LAST_SUCCESS = "st"  # last success timestamp
    ATTR_RUNS = "runs"  # Number of runs
    ATTR_FAULTS = "f"  # Amount of sequental faults
    ATTR_OFFSET = "o"  # Random offset [0 .. 1]

    # Job states
    S_WAIT = "W"  # Waiting to run
    S_RUN = "R"   # Running
    S_STOP = "S"  # Stopped by operator
    S_DISABLED = "D"  # Disabled by system
    S_SUSPEND = "s"  # Suspended by system

    # Exit statuses
    E_SUCCESS = "S"  # Completed successfully
    E_FAILED = "F"  # Failed
    E_EXCEPTION = "X"  # Terminated by exception
    E_DEFERRED = "D"  # Cannot be run
    E_DEREFERENCE = "d"  # Cannot be dereferenced

    STATUS_MAP = {
        E_SUCCESS: "SUCCESS",
        E_FAILED: "FAILED",
        E_EXCEPTION: "EXCEPTION",
        E_DEFERRED: "DEFERRED",
        E_DEREFERENCE: "DEREFERENCE"
    }

    class JobFailed(Exception):
        pass

    # List of exceptions to be considered failed jobs
    failed_exceptions = (JobFailed,)

    def __init__(self, scheduler, attrs):
        """
        :param scheduler: Scheduler instance
        :param attrs: dict containing record from scheduler's collection
        """
        self.scheduler = scheduler
        self.attrs = attrs
        self.object = None
        self.start_time = None
        self.duration = None
        self.logger = PrefixLoggerAdapter(
            scheduler.logger,
            self.get_display_key()
        )
        self.context = {}

    def load_context(self, data):
        self.context = data or {}
        self.init_context()

    def init_context(self):
        """
        Perform context initialization
        """
        pass

    @tornado.gen.coroutine
    def run(self):
        self.start_time = time.time()
        self.logger.info(
            "[%s] Starting at %s (Lag %.2fms)",
            self.name,
            self.scheduler.scheduler_id,
            total_seconds(
                datetime.datetime.now() - self.attrs[self.ATTR_TS]
            ) * 1000.0
        )
        # Run handler
        status = self.E_EXCEPTION
        try:
            ds = self.dereference()
            can_run = self.can_run()
        except Exception as e:
            self.logger.error("Unknown error during dereference: %s", e)
            ds = None
            can_run = False

        if ds:
            if can_run:
                try:
                    data = self.attrs.get(self.ATTR_DATA) or {}
                    result = self.handler(**data)
                    if tornado.gen.is_future(result):
                        # Wait for future
                        result = yield result
                    status = self.E_SUCCESS
                except self.failed_exceptions:
                    status = self.E_FAILED
                except Exception:
                    error_report()
                    status = self.E_EXCEPTION
            else:
                self.logger.info("Deferred")
                status = self.E_DEFERRED
        elif ds is not None:
            self.logger.info("Cannot dereference")
            status = self.E_DEREFERENCE
        self.duration = time.time() - self.start_time
        self.logger.info("Completed. Status: %s (%.2fms)",
                         self.STATUS_MAP.get(status, status),
                         self.duration * 1000)
        # Schedule next run
        self.schedule_next(status)

    def handler(self, **kwargs):
        """
        Job handler, must be sublclassed
        """
        raise NotImplementedError()

    def get_defererence_query(self):
        """
        Get dereference query condition.
        Called by dereference()
        :return: dict or None
        """
        return {"pk": self.attrs[self.ATTR_KEY]}

    def dereference(self):
        """
        Retrieve referenced object from database
        """
        if self.model and self.use_get_by_id:
            self.object = self.model.get_by_id(self.attrs[self.ATTR_KEY])
            if not self.object:
                return False
        elif self.model:
            q = self.get_defererence_query()
            if q is None:
                return False
            try:
                # Resolve object
                self.object = self.model.objects.get(**q)
            except self.model.DoesNotExist:
                return False
        # Adjust logging
        self.logger.set_prefix(
            "%s][%s][%s" % (
                self.scheduler.name,
                self.name,
                self.get_display_key()
            )
        )
        return True

    def get_display_key(self):
        """
        Return dereferenced key name
        """
        if self.object:
            return unicode(self.object)
        else:
            return self.attrs[self.ATTR_KEY]

    def can_run(self):
        """
        Check wrether the job can be launched
        :return:
        """
        return True

    def get_group(self):
        return self.group_name

    def remove_job(self):
        """
        Remove job from schedule
        """
        self.scheduler.remove_job_by_id(self.attrs[self.ATTR_ID])

    def schedule_next(self, status):
        """
        Schedule next run depending on status.
        Drop job by default
        """
        self.remove_job()

    @classmethod
    def submit(cls, scheduler, name=None,
               key=None, data=None, pool=None,
               ts=None, delta=None, keep_ts=False):
        """
        Submit new job or change schedule for existing one
        :param scheduler: scheduler name
        :param name: Job full name
        :param key: Job key
        :param data: Job data
        :param pool: Pool name
        :param ts: Next run timestamp
        :param delta: Run after *delta* seconds
        :param keep_ts: Do not touch timestamp of existing jobs,
            set timestamp only for created jobs
        """
        from .scheduler import Scheduler
        scheduler = Scheduler(
            name=scheduler,
            pool=pool
        )
        scheduler.submit(
            name,
            key=key,
            data=data,
            ts=ts,
            delta=delta,
            keep_ts=keep_ts
        )

    @classmethod
    def remove(cls, scheduler, name=None, key=None, pool=None):
        from .scheduler import Scheduler
        scheduler = Scheduler(
            name=scheduler,
            pool=pool
        )
        scheduler.remove_job(name, key=key)

    @classmethod
    def get_job_data(cls, scheduler, jcls, key=None, pool=None):
        from .scheduler import Scheduler
        scheduler = Scheduler(
            name=scheduler,
            pool=pool
        )
        return scheduler.get_collection().find_one({
            Job.ATTR_CLASS: jcls,
            Job.ATTR_KEY: key
        })

    def get_context_cache_key(self):
        ctx = {
            "name": self.scheduler.name,
            "pool": self.scheduler.pool or "global",
            "job_id": self.attrs[self.ATTR_ID]
        }
        return self.context_cache_key % ctx
