# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-notifier plugins
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import Queue
import logging
import datetime
## NOC modules
from noc.lib.registry import Registry
from noc.lib.debug import error_report


class NotifyRegistry(Registry):
    name = "NotifyRegistry"
    subdir = "notify"
    classname = "Notify"
    apps = ["noc.main"]

notify_registry = NotifyRegistry()


class NotifyBase(type):
    """
    Notify metaclass
    """
    def __new__(cls, name, bases, attrs):
        m = type.__new__(cls, name, bases, attrs)
        notify_registry.register(m.name, m)
        return m


class Notify(object):
    """
    Notify base class
    """
    __metaclass__ = NotifyBase
    name = None

    def __init__(self, parent):
        self.info("Initializing")
        self.parent = parent
        self.task_queue = Queue.Queue()
        self.max_queue_size = self.config.getint(self.name,
                                                 "queue_size")
        self.ttl = datetime.timedelta(
            seconds=self.config.getint(self.name,"time_to_live"))
        self.retry_interval = datetime.timedelta(
            seconds=self.config.getint(self.name, "retry_interval"))

    @property
    def config(self):
        return self.parent.config

    def debug(self, message):
        logging.debug("[%s] %s" % (self.name, message))

    def info(self, message):
        logging.info("[%s] %s" % (self.name, message))

    def error(self, message):
        logging.error("[%s] %s" % (self.name, message))

    def can_queue(self):
        """
        Has the task queue free space?
        :return:
        """
        return self.task_queue.qsize() < self.max_queue_size

    def new_task(self, task_id, params, subject, body, link=None):
        """
        Called by daemon to spool new task
        :param task_id:
        :param params:
        :param subject:
        :param body:
        :param link:
        :return:
        """
        self.task_queue.put((task_id, params, subject, body, link))

    def run(self):
        """
        Worker loop, executed in separate thread
        :return:
        """
        while True:
            task_id, params, subject, body, link = self.task_queue.get()
            try:
                status = self.send_message(params, subject, body, link)
            except:
                error_report()
                self.parent.on_task_complete(task_id, False)
                continue
            s = {True: "OK", False: "ERROR"}[status]
            self.info("SENDING id=%s status=%s to=%s subject=%s" % (
                task_id, s, params, subject))
            if status:
                self.parent.on_task_complete(task_id, status)
            else:
                self.parent.on_task_complete(task_id, status,
                    next_try=datetime.datetime.now() + self.retry_interval)

    def send_message(self, params, subject, body, link=None):
        """
        Send message. Overloaded by notification plugins
        :param params:
        :param subject:
        :param body:
        :param link:
        :return:
        """
        return True
