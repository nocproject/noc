# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Scheduler Job Class
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging


class Job(object):
    """
    Basic scheduler job class.
    """
    name = ""  # Unique Job name
    map_task = None  # Set to map task name

    S_SUCCESS = 0
    S_FAILED = 1
    S_EXCEPTION = 2

    JOB_NS = "_noc"  # data structure prefix to be placed to _local

    def __init__(self, scheduler, key=None, data=None):
        self.scheduler = scheduler
        self.key = key
        self.data = data or {}
        self.job_data = self.data.get(self.JOB_NS, {})

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

    def get_map_task_params(self):
        """
        Return dict containing job's MRT params
        (applicable only when map_task is not None)
        :return:
        """
        return {}
