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


class SchedulerDaemon(Daemon):
    daemon_name = "noc-scheduler"

    def __init__(self):
        super(SchedulerDaemon, self).__init__()
        logging.info("Running noc-scheduler")
        self.periodic_thread = None

    def run(self):
        self.periodic_thread = PeriodicScheduler(self)
        self.periodic_thread.start()
        while True:
            self.periodic_thread.join(1)
            if not self.periodic_thread.isAlive():
                break
