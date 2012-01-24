# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-scheduler daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
from __future__ import with_statement
import os
import time
import datetime
import logging
import threading
## Django modules
from django.db import transaction, reset_queries
## NOC modules
from noc.lib.daemon import Daemon
from noc.lib.periodic import periodic_registry
from noc.lib.debug import error_report
from noc.main.models import Schedule, TimePattern, PyRule
from noc.sa.models import ManagedObject
from noc.fm.models import NewEvent


class Scheduler(Daemon):
    daemon_name = "noc-scheduler"

    def __init__(self):
        super(Scheduler, self).__init__()
        logging.info("Running noc-scheduler")
        self.running = set()
        self.running_lock = threading.Lock()

    def update_schedules(self):
        """Create schedules for new periodic tasks"""
        # Get or create Any time pattern
        tp, created = TimePattern.objects.get_or_create(name="Any")
        #
        for pt in periodic_registry.classes:
            if not Schedule.objects.filter(periodic_name=pt).exists():
                logging.info("Creating schedule for %s" % pt)
                Schedule(
                    periodic_name=pt,
                    is_enabled=False,
                    time_pattern=tp,
                    timeout=periodic_registry[pt].default_timeout
                ).save()

    def launch_task(self, task):
        """
        Launch new periodic task
        """
        with self.running_lock:
            self.running.add(task.periodic_name)
        threading.Thread(name=unicode(task).encode("utf8"),
                         target=self.task_wrapper,
                         kwargs={"task": task}).start()

    def task_wrapper(self, task):
        """Periodic thread target"""
        logging.info(u"Periodic task=%s status=running" % unicode(task))
        t = datetime.datetime.now()
        cwd = os.getcwd()
        try:
            if task.periodic_name.startswith("pyrule:"):
                status = PyRule.call(task.periodic_name[7:],
                                     timeout=task.timeout)
            else:
                status = task.periodic(task.timeout).execute()
        except:
            error_report()
            status = False
        logging.info(u"Periodic task=%s status=%s" % (unicode(task),
                                        "completed" if status else "failed"))
        # Current path may be implicitly changed by periodic. Restore old value
        # to prevent further bugs
        new_cwd = os.getcwd()
        if cwd != new_cwd:
            logging.error("CWD changed by periodic '%s' ('%s' -> '%s'). Restoring old cwd" % (unicode(task), cwd, new_cwd))
            os.chdir(cwd)
        # Mark task results
        try:
            nt = Schedule.objects.get(id=task.id)
            nt.mark_run(t, status)
        except Schedule.DoesNotExist:
            pass  # Scheule deleted during task run
        with self.running_lock:
            self.running.remove(task.periodic_name)
        # Create appropriative FM event
        self.write_event([
            ("source", "system"),
            ("type", "periodic status"),
            ("task", unicode(task)),
            ("status", {True: "success", False: "failure"}[status]),
        ])

    def write_event(self, data, timestamp=None):
        """
        Write FM event

        :param data: List of (left, right)
        :type data: list
        """
        if timestamp is None:
            timestamp = datetime.datetime.now()
        NewEvent(
            timestamp = timestamp,
            managed_object = ManagedObject.objects.get(name="SAE"),
            raw_vars = dict(data),
            log = []
        ).save()

    def run(self):
        # Wait for 15 seconds
        logging.info("Waiting for 15 seconds")
        for i in range(15):
            time.sleep(1)
            self.heartbeat()
        transaction.enter_transaction_management()
        self.update_schedules()
        while True:
            self.heartbeat()
            last_check = time.time()
            # Get tasks to run
            new_tasks = Schedule.get_tasks()
            to_run = []
            with self.running_lock:
                for t in new_tasks:
                    # Check task not running
                    if t.periodic_name in self.running:
                        continue
                    # Check for blocking tasks
                    if not t.periodic_name.startswith("pyrule:"):
                        i = self.running.intersection(set(t.periodic.wait_for))
                        if i:
                            logging.info("Periodic task '%s' cannot be launched when %s is active" %
                                        (t.periodic_name, ", ".join(i)))
                            continue
                    to_run += [t]
            # Launch tasks
            for t in to_run:
                self.launch_task(t)
            transaction.commit()
            reset_queries()
            time.sleep(max(0, 1.0 - time.time() + last_check))
        transaction.leave_transaction_management()
