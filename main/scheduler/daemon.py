# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Legacy periodic scheduler
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
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

    def run(self):
        self.scheduler = JobScheduler(self)
        self.periodic_thread = PeriodicScheduler(self)
        self.periodic_thread.start()
        self.scheduler.run()
