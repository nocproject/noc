# ----------------------------------------------------------------------
# Scheduler Job Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import time
import datetime
from time import perf_counter
import asyncio

# Third-party modules
from typing import Dict, Any

# NOC modules
from noc.core.log import PrefixLoggerAdapter
from noc.core.debug import error_report
from .error import RetryAfter
from noc.core.span import Span
from noc.core.comp import smart_text

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
    ATTR_MAX_RUNS = "mruns"  # Maximum allowed number of runs
    ATTR_FAULTS = "f"  # Amount of sequental faults
    ATTR_OFFSET = "o"  # Random offset [0 .. 1]
    ATTR_SAMPLE = "sample"  # Span sample
    ATTR_SHARD = "shard"  # Sharding key

    # Job states
    S_WAIT = "W"  # Waiting to run
    S_RUN = "R"  # Running
    S_STOP = "S"  # Stopped by operator
    S_DISABLED = "D"  # Disabled by system
    S_SUSPEND = "s"  # Suspended by system
    S_POSTPONED = "P"  # Postponed until next restart

    # Exit statuses
    E_SUCCESS = "S"  # Completed successfully
    E_FAILED = "F"  # Failed
    E_EXCEPTION = "X"  # Terminated by exception
    E_DEFERRED = "D"  # Cannot be run
    E_DEREFERENCE = "d"  # Cannot be dereferenced
    E_RETRY = "r"  # Forcefully retried

    STATUS_MAP = {
        E_SUCCESS: "SUCCESS",
        E_FAILED: "FAILED",
        E_EXCEPTION: "EXCEPTION",
        E_DEFERRED: "DEFERRED",
        E_DEREFERENCE: "DEREFERENCE",
        E_RETRY: "RETRY",
    }

    # List of contexts should be initialized
    default_contexts = None

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
        self.logger = PrefixLoggerAdapter(scheduler.logger, self.get_display_key())
        self.context: Dict[str, Any] = {}

    def load_context(self, data):
        self.context = data or {}
        self.init_context()

    def init_context(self):
        """
        Perform context initialization
        """
        if not self.default_contexts:
            return
        for ctx in self.default_contexts:
            if ctx not in self.context:
                self.context[ctx] = {}

    def run(self):
        with Span(
            server=self.scheduler.name,
            service=self.attrs[self.ATTR_CLASS],
            sample=self.attrs.get(self.ATTR_SAMPLE, 0),
            in_label=self.attrs.get(self.ATTR_KEY, ""),
        ):
            self.start_time = perf_counter()
            if self.is_retries_exceeded():
                self.logger.info(
                    "[%s|%s] Retries exceeded. Remove job", self.name, self.attrs[Job.ATTR_ID]
                )
                self.remove_job()
                return
            self.logger.info(
                "[%s] Starting at %s (Lag %.2fms)",
                self.name,
                self.scheduler.scheduler_id,
                (datetime.datetime.now() - self.attrs[self.ATTR_TS]).total_seconds() * 1000.0,
            )
            # Run handler
            status = self.E_EXCEPTION
            delay = None
            with Span(service="job.dereference"):
                try:
                    ds = self.dereference()
                    can_run = self.can_run()
                except Exception as e:
                    self.logger.error("Unknown error during dereference: %s", e)
                    ds = None
                    can_run = False

            if ds:
                with Span(service="job.run"):
                    if can_run:
                        try:
                            data = self.attrs.get(self.ATTR_DATA) or {}
                            result = self.handler(**data)
                            if asyncio.isfuture(result):
                                # Wait for future
                                for _ in asyncio.as_completed([result]):
                                    pass
                            status = self.E_SUCCESS
                        except RetryAfter as e:
                            self.logger.info("Retry after %ss: %s", e.delay, e)
                            status = self.E_RETRY
                            delay = e.delay
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
            self.duration = perf_counter() - self.start_time
            self.logger.info(
                "Completed. Status: %s (%.2fms)",
                self.STATUS_MAP.get(status, status),
                self.duration * 1000,
            )
            # Schedule next run
            if delay is None:
                with Span(service="job.schedule_next"):
                    self.schedule_next(status)
            else:
                with Span(service="job.schedule_retry"):
                    # Retry
                    if self.context_version:
                        ctx = self.context or None
                        ctx_key = self.get_context_cache_key()
                    else:
                        ctx = None
                        ctx_key = None
                    self.scheduler.set_next_run(
                        self.attrs[self.ATTR_ID],
                        status=status,
                        ts=datetime.datetime.now() + datetime.timedelta(seconds=delay),
                        duration=self.duration,
                        context_version=self.context_version,
                        context=ctx,
                        context_key=ctx_key,
                    )

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
            "%s][%s][%s" % (self.scheduler.name, self.name, self.get_display_key())
        )
        return True

    def get_display_key(self):
        """
        Return dereferenced key name
        """
        if self.object:
            return smart_text(self.object)
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
    def submit(
        cls,
        scheduler,
        name=None,
        key=None,
        data=None,
        pool=None,
        ts=None,
        delta=None,
        keep_ts=False,
        shard=None,
    ):
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
        :param shard:
        """
        from .scheduler import Scheduler

        scheduler = Scheduler(name=scheduler, pool=pool)
        scheduler.submit(name, key=key, data=data, ts=ts, delta=delta, keep_ts=keep_ts, shard=shard)

    @classmethod
    def remove(cls, scheduler, name=None, key=None, pool=None):
        from .scheduler import Scheduler

        scheduler = Scheduler(name=scheduler, pool=pool)
        scheduler.remove_job(name, key=key)

    @classmethod
    def get_job_data(cls, scheduler, jcls, key=None, pool=None):
        from .scheduler import Scheduler

        scheduler = Scheduler(name=scheduler, pool=pool)
        return scheduler.get_collection().find_one({Job.ATTR_CLASS: jcls, Job.ATTR_KEY: key})

    def get_context_cache_key(self):
        ctx = {
            "name": self.scheduler.name,
            "pool": self.scheduler.pool or "global",
            "job_id": self.attrs[self.ATTR_ID],
        }
        return self.context_cache_key % ctx

    @classmethod
    def retry_after(cls, delay, msg=""):
        """
        Must be called from job handler to deal with temporary problems.
        Current job handler will be terminated and job
        will be scheduled after *delay* seconds
        :param delay: Delay in seconds
        :param msg: Informational message
        :return:
        """
        raise RetryAfter(msg, delay=delay)

    def is_retries_exceeded(self):
        """
        Check if maximal amount of retries is exceeded
        :return:
        """
        runs = self.attrs.get(Job.ATTR_RUNS, 0)
        max_runs = self.attrs.get(Job.ATTR_MAX_RUNS, 0)
        return max_runs and runs >= max_runs

    @staticmethod
    def get_next_timestamp(interval, offset=0.0, ts=None):
        """
        Calculate next timestamp
        :param interval:
        :param offset:
        :param ts: current timestamp
        :return: datetime object
        """
        if not ts:
            ts = time.time()
        if ts and isinstance(ts, datetime.datetime):
            ts = time.mktime(ts.timetuple()) + float(ts.microsecond) / 1000000.0
        # Get start of current interval
        si = ts // interval * interval
        # Shift to offset
        si += offset * interval
        # Shift to interval if in the past
        if si <= ts:
            si += interval
        return datetime.datetime.fromtimestamp(si)

    def get_runs(self) -> int:
        return self.attrs.get(Job.ATTR_RUNS, 0)
