## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-discovery daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from scheduler import DiscoveryScheduler
from noc.lib.daemon import Daemon


class DiscoveryDaemon(Daemon):
    daemon_name = "noc-discovery"

    def __init__(self, *args, **kwargs):
        super(DiscoveryDaemon, self).__init__(*args, **kwargs)
        self.scheduler = DiscoveryScheduler(self)

    def run(self):
        self.scheduler.run()

#    def report_address_collisions(self):
#        ctx = {
#            "count": len(self.address_collisions),
#            "collisions": [
#                {
#                    "address": address,
#                    "vrf_old": vrf1,
#                    "vrf_new": vrf2,
#                    "object_old": o1,
#                    "object_new": o2,
#                    "interface_new": i2
#                }
#                for address, vrf1, o1, vrf2, o2, i2
#                in self.address_collisions
#            ]
#        }
#        self.send_report("inv.discovery.address_collision_report", ctx)
