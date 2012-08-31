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
    map_task = None  # Set to map task name
    model = None  # Model/Document class
    system_notification = None  # Name of system notification group

    S_SUCCESS = "S"
    S_FAILED = "F"
    S_EXCEPTION = "X"

    JOB_NS = "_noc"  # data structure prefix to be placed to _local

    def __init__(self, scheduler, key=None, data=None):
        self.scheduler = scheduler
        self.key = key
        self.data = data or {}
        self.object = None  # Set by dereference()
        self.job_data = self.data.get(self.JOB_NS, {})
        self.started = None  # Timestamp
        self._log = []

    def info(self, msg):
        logging.info("[%s: %s(%s)] %s" % (
            self.scheduler.name, self.name, self.key, msg))

    def error(self, msg):
        logging.error("[%s: %s(%s)] %s" % (
            self.scheduler.name, self.name, self.key, msg))

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
        return None  # Remove schedule on complete

    @classmethod
    def submit(cls, scheduler, key, data=None,
               ts=None):
        scheduler.submit(cls.name, key, data, ts)

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

    def dereference(self):
        if self.model:
            try:
                self.object = self.model.objects.get(id=self.key)
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
