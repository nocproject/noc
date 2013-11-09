# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Scheduler Job Class
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import datetime
import random
## NOC modules
from noc.main.models import SystemNotification


class JobBase(type):
    def __new__(cls, name, bases, attrs):
        m = type.__new__(cls, name, bases, attrs)
        if m.map_task and not m.model:
            from noc.sa.models import ManagedObject
            m.model = ManagedObject
        return m


class Job(object):
    """
    Basic scheduler job class.

    Model/Document dereference:
    If *model* parameter is set to Module or Document class,
    *key* will be dereferenced and *object* attribute will be set.

    MRT mode:
    if *map_task* is set, *get_map_task_params()* will be called
    to get task parameters, then MRT will be launched.
    *handler* function will be called on MRT successful completion.
    """
    __metaclass__ = JobBase
    name = ""  # Unique Job name
    ignored = False  # Set to True to ignore job class
    map_task = None  # Set to map task name
    model = None  # Model/Document class
    system_notification = None  # Name of system notification group
    concurrency = None  # Limit number of concurrently running jobs
    threaded = False  # Run handler in separate thread
    max_delay = 0  # When set, consider task delayed more than
                   # max delay seconds as late
    delay_interval = 0  # Postpone late tasks to random 0..delay_interval
                        # seconds
    S_SUCCESS = "S"
    S_FAILED = "F"
    S_EXCEPTION = "X"
    S_DEFERRED = "D"
    S_LATE = "L"

    group = None
    beef = {}  # key -> result for MRT tasks

    def __init__(self, scheduler, key=None, data=None, schedule=None):
        self.scheduler = scheduler
        self.key = key
        self.data = data or {}
        self.schedule = schedule or {}
        self.object = None  # Set by dereference()
        self.started = None  # Timestamp
        self._log = []
        self.on_complete = []  # List of (job_name, key)
                               # to launch on complete

    @classmethod
    def initialize(cls, scheduler):
        """
        Called on scheduler.register()
        :param cls:
        :param scheduler:
        :return:
        """
        pass

    @classmethod
    def set_beef(cls, beef):
        cls.beef = beef

    def get_display_key(self):
        return self.key

    def debug(self, msg):
        logging.debug("[%s: %s(%s)] %s" % (
            self.scheduler.name, self.name,
            self.get_display_key(), msg))

    def info(self, msg):
        logging.info("[%s: %s(%s)] %s" % (
            self.scheduler.name, self.name,
            self.get_display_key(), msg))

    def error(self, msg):
        logging.error("[%s: %s(%s)] %s" % (
            self.scheduler.name, self.name,
            self.get_display_key(), msg))

    def handler(self, *args, **kwargs):
        """
        Job handler. Returns True on success, False on failure
        or raise exception. Depending on result, on_success,
        on_failure or on_exception
        """
        return True

    def on_success(self):
        """
        Called when handler returns True
        :return:
        """
        pass

    def on_failure(self):
        """
        Called when handler returns False
        :return:
        """
        pass

    def on_exception(self):
        """
        Called when handler raises an error
        :return:
        """
        pass

    def get_schedule(self, status):
        """
        Called by scheduler to get next run time
        :status: Job.S_*
        :return:
        """
        if status == self.S_LATE and self.delay_interval:
            return (datetime.datetime.now() +
                    datetime.timedelta(
                        seconds=random.random() * self.delay_interval))
        return None  # Remove schedule on complete

    @classmethod
    def submit(cls, scheduler, key, data=None, schedule=None,
               ts=None):
        scheduler.submit(cls.name, key=key, data=data,
            schedule=schedule, ts=ts)

    def get_managed_object(self):
        """
        Return managed object instance or id
        (applicable only when map_task is not None)
        :return:
        """
        return self.key

    def get_map_task_params(self):
        """
        Return dict containing job's MRT params
        (applicable only when map_task is not None)
        :return:
        """
        return {}

    def get_defererence_query(self):
        """
        Get dereference query condition.
        Called by dereference()
        :return: dict or None
        """
        return {"id": self.key}

    def dereference(self):
        if self.model:
            q = self.get_defererence_query()
            if q is None:
                return False
            try:
                self.object = self.model.objects.get(**q)
            except self.model.DoesNotExist:
                return False
        return True

    def notify(self, subject, body):
        SystemNotification.notify(
            name=self.system_notification,
            subject=subject,
            body=body)

    def log(self, msg):
        self._log += [{
            "t": datetime.datetime.now(),
            "m": msg
        }]

    def get_log(self):
        return self._log

    def can_run(self):
        """
        Check wrether the job can be launched
        :return:
        """
        return True

    def run_on_complete(self, job_name, key):
        j = (job_name, key)
        if j not in self.on_complete:
            self.on_complete += [j]

    def get_group(self):
        return self.group
