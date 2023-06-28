# ----------------------------------------------------------------------
# Cron Job Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.scheduler.periodicjob import PeriodicJob
from noc.core.topology.uplink import update_uplinks
from noc.core.change.policy import change_tracker
from noc.config import config


class TopologyUplinksJob(PeriodicJob):
    def handler(self, **kwargs):
        self.logger.info("Run update Objects Uplinks")
        with change_tracker.bulk_changes():
            update_uplinks()

    def can_run(self):
        return config.topo.enable_scheduler_task

    def get_interval(self):
        """
        Returns next repeat interval
        """
        return config.topo.interval
