# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Legacy periodic scheduler
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import time
## NOC modules
from noc.lib.daemon import Daemon
from periodic import PeriodicScheduler
from scheduler import JobScheduler


class SchedulerDaemon(Daemon):
    daemon_name = "noc-scheduler"
    use_solutions = True

    def __init__(self):
        self.start_delay = 0
        super(SchedulerDaemon, self).__init__()
        logging.info("Running noc-scheduler")
        self.periodic_thread = None
        self.scheduler = None

    def load_config(self):
        super(SchedulerDaemon, self).load_config()
        if self.config.has_option("main", "start_delay"):
            self.start_delay = self.config.getint("main", "start_delay")

    def run(self):
        if self.start_delay:
            self.logger.info("Delaying start for %s seconds",
                             self.start_delay)
            time.sleep(self.start_delay)
        self.scheduler = JobScheduler(self)
        self.periodic_thread = PeriodicScheduler(self)
        self.periodic_thread.start()
        self.scheduler.run()
