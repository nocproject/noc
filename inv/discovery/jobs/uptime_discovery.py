## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Uptime discovery jobs
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import MODiscoveryJob
from noc.settings import config
from noc.fm.models.uptime import Uptime


class UptimeDiscoveryJob(MODiscoveryJob):
    name = "uptime_discovery"
    map_task = "get_uptime"

    ignored = not config.getboolean("uptime_discovery", "enabled")

    def handler(self, object, result):
        """
        :param object:
        :param result:
        :return:
        """
        self.logger.info("Received uptime %s", result)
        if result:
            Uptime.register(self.object, result)
        return True

    def can_run(self):
        return (super(UptimeDiscoveryJob, self).can_run()
                and self.object.object_profile.enable_uptime_discovery)

    def get_failed_interval(self):
        return self.object.object_profile.uptime_discovery_min_interval
