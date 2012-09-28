# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Legacy periodic scheduler
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
from __future__ import with_statement
import logging
## NOC modules
from noc.lib.daemon import Daemon
from periodic import PeriodicScheduler
from scheduler import JobScheduler


class SchedulerDaemon(Daemon):
    daemon_name = "noc-scheduler"

    def __init__(self):
        super(SchedulerDaemon, self).__init__()
        logging.info("Running noc-scheduler")
        self.periodic_thread = None
        self.scheduler = None

    def run(self):
        self.scheduler = JobScheduler(self)
        self.periodic_thread = PeriodicScheduler(self)
        self.periodic_thread.start()
        self.scheduler.run()
        # Wait for periodic thread termination
        # while True:
        #    self.periodic_thread.join(1)
        #    if not self.periodic_thread.isAlive():
        #        break
