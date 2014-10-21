# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Legacy periodic scheduler
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import logging
## NOC modules
from noc.lib.daemon import Daemon
from periodic import PeriodicScheduler
from scheduler import JobScheduler


class SchedulerDaemon(Daemon):
    daemon_name = "noc-scheduler"
    use_solutions = True

    def __init__(self):
        super(SchedulerDaemon, self).__init__()
        logging.info("Running noc-scheduler")
        self.periodic_thread = None
        self.scheduler = None

    def load_config(self):
        super(SchedulerDaemon, self).load_config()

    def run(self):
        self.scheduler = JobScheduler(self)
        self.periodic_thread = PeriodicScheduler(self)
        self.periodic_thread.start()
        self.scheduler.run()
