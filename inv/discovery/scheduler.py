## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-discovery scheduler
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import datetime
import random
## NOC modules
from noc.lib.scheduler.scheduler import Scheduler
from noc.lib.solutions import solutions_roots


class DiscoveryScheduler(Scheduler):
    def __init__(self, daemon=None):
        self.daemon = daemon
        super(DiscoveryScheduler, self).__init__(
            "inv.discovery", initial_submit=daemon is not None,
            reset_running=daemon is not None
        )
        self.register_all(
            os.path.join("inv", "discovery", "jobs"),
            exclude=["base.py"])
        for r in solutions_roots():
            jd = os.path.join(r, "discovery", "jobs")
            if os.path.isdir(jd):
                self.register_all(jd)

    def can_run(self, job):
        group = job.get_group()
        if group is not None:
            with self.running_lock:
                return group not in self.running_count
        return True

    def ensure_job(self, job_name, managed_object):
        """
        Ensure job is scheduled. Create if not
        :param job_name:
        :param managed_object:
        :return: True if new job has been scheduled
        """
        j = self.get_job(job_name, managed_object.id)
        if not j:
            jcls = self.job_classes[job_name]
            if jcls.can_submit(managed_object):
                s_interval = jcls.get_submit_interval(managed_object)
                if s_interval:
                    jcls.submit(
                        scheduler=self, key=managed_object.id,
                        interval=s_interval,
                        failed_interval=s_interval,
                        randomize=True,
                        ts=datetime.datetime.now() + datetime.timedelta(
                            seconds=random.random() * jcls.initial_submit_interval)
                    )
                    return True
        return False
