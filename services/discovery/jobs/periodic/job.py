# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Periodic Discovery Job
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.services.discovery.jobs.base import MODiscoveryJob
from uptime import UptimeCheck
from interfacestatus import InterfaceStatusCheck
from mac import MACCheck


class PeriodicDiscoveryJob(MODiscoveryJob):
    name = "periodic"

    def handler(self, **kwargs):
        if self.object.object_profile.enable_periodic_discovery_uptime:
            UptimeCheck(self).run()
        if self.object.object_profile.enable_periodic_discovery_interface_status:
            InterfaceStatusCheck(self).run()
        if self.object.object_profile.enable_periodic_discovery_mac:
            MACCheck(self).run()

    def can_run(self):
        return (
            self.object.is_managed and
            self.object.object_profile.enable_periodic_discovery and
            self.object.object_profile.periodic_discovery_interval
        )

    def get_interval(self):
        return self.object.object_profile.periodic_discovery_interval

    def get_failed_interval(self):
        return self.object.object_profile.periodic_discovery_interval
