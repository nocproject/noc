## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-discovery scheduler
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import logging
## NOC modules
from noc.lib.scheduler.scheduler import Scheduler
from noc.lib.solutions import solutions_roots
from utils import get_active_discovery_methods

logger = logging.getLogger(__name__)


class DiscoveryScheduler(Scheduler):
    CAPS_REQUIRED = {}  # method -> required caps

    def __init__(self, daemon=None, max_threads=None):
        self.daemon = daemon
        super(DiscoveryScheduler, self).__init__(
            "inv.discovery", initial_submit=daemon is not None,
            reset_running=daemon is not None,
            max_threads=None if daemon else 0
        )
        self.register_all(
            os.path.join("inv", "discovery", "jobs"),
            exclude=["base.py"])
        for r in solutions_roots():
            jd = os.path.join(r, "discovery", "jobs")
            if os.path.isdir(jd):
                self.register_all(jd)

    def can_run(self, job):
        if not super(DiscoveryScheduler, self).can_run(job):
            return False
        group = job.get_group()
        if group is not None:
            with self.running_lock:
                return group not in self.running_count
        return True

    def register_job_class(self, cls):
        super(DiscoveryScheduler, self).register_job_class(cls)
        if cls.name and hasattr(cls, "required_caps") and cls.required_caps:
            self.CAPS_REQUIRED[cls.name] = cls.required_caps

    def get_effective_jobs(self, object):
        """
        Get effective jobs for managed object
        """
        caps = object.get_caps()
        jls = []
        for j in get_active_discovery_methods():
            job = self.job_classes[j]
            if job.map_task and not job.map_task in object.profile.scripts:
                continue  # No appropriative script
            meet = True
            if j in self.CAPS_REQUIRED:
                for c in self.CAPS_REQUIRED[j]:
                    if not caps.get(c):
                        meet = False
                        break
            if meet:
                jls += [j]
        return jls

    def ensure_jobs(self, object, status=True):
        """
        Ensure managed object's jobs according to status
        """
        suspend_jobs = set(get_active_discovery_methods())
        if status:
            effective_jobs = set(self.get_effective_jobs(object))
            suspend_jobs -= effective_jobs
        else:
            effective_jobs = set()
        if not suspend_jobs and not effective_jobs:
            return
        if suspend_jobs:
            self.logger.info("Suspending jobs for %s: %s",
                             object.name, ", ".join(suspend_jobs))
        if effective_jobs:
            self.logger.info("Resuming jobs for %s: %s",
                             object.name, ", ".join(effective_jobs))
        bulk = self.collection.initialize_unordered_bulk_op()
        if suspend_jobs:
            bulk.find({
                self.ATTR_KEY: object.id,
                self.ATTR_STATUS: self.S_WAIT,
                self.ATTR_CLASS: {
                    "$in": list(suspend_jobs)
                }
            }).update({
                "$set": {
                    self.ATTR_STATUS: self.S_SUSPEND
                }
            })
        if effective_jobs:
            bulk.find({
                self.ATTR_KEY: object.id,
                self.ATTR_STATUS: self.S_SUSPEND,
                self.ATTR_CLASS: {
                    "$in": list(effective_jobs)
                }
            }).update({
                "$set": {
                    self.ATTR_STATUS: self.S_WAIT
                }
            })
        bulk.execute()

    @classmethod
    def on_change_object_caps(cls, object):
        logger.info("Applying changes to object capabilities '%s'",
                    object.name)
        get_scheduler().ensure_jobs(object, status=object.get_status())

_scheduler = None


def get_scheduler():
    global _scheduler
    if not _scheduler:
        _scheduler = DiscoveryScheduler()
    return _scheduler
