# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Job scheduler
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
from collections import defaultdict
## NOC modules
from noc.lib.scheduler.scheduler import Scheduler
from jobs.subscriber import SubscriberJob
from noc.settings import INSTALLED_APPS
from noc.lib.solutions import solutions_roots


class JobScheduler(Scheduler):
    def __init__(self, daemon=None):
        self.daemon = daemon
        super(JobScheduler, self).__init__(
            "main.jobs",
            initial_submit=daemon is not None,
            reset_running=daemon is not None,
            max_threads=daemon.config.getint("main", "max_threads")
        )
        # Subscribers
        self.subscribers = defaultdict(list)  # Destination -> [jobs]
        # Install application jobs
        for app in INSTALLED_APPS:
            if not app.startswith("noc."):
                continue
            p = app.split(".")[1:] + ["jobs"]
            pp = os.path.join(*p)
            if os.path.isdir(pp):
                self.register_all(pp)
        for r in solutions_roots():
            jd = os.path.join(r, "jobs")
            if os.path.isdir(jd):
                self.register_all(jd)

    def register_job_class(self, cls):
        if issubclass(cls, SubscriberJob):
            job = cls(self)
            dst = job.get_destination()
            self.info("Subscribing job class %s to %s" % (
                job.name, dst))
            self.subscribers[dst] += [job]
            self.daemon.stomp_client.subscribe(dst, self.on_msg)
        else:
            return super(JobScheduler, self).register_job_class(cls)

    def on_msg(self, destination, body):
        """
        Respond to STOMP messages
        :param destination:
        :param body:
        :return:
        """
        self.debug("Receiving STOMP message to destination %s: %r" % (
            destination, body))
        # @todo: threaded
        if destination in self.subscribers:
            for job in self.subscribers[destination]:
                job.handler(destination, body)
