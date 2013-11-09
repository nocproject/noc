## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-discovery daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from collections import defaultdict
import os
import logging
## NOC modules
from scheduler import DiscoveryScheduler
from noc.lib.daemon import Daemon
from jobs.performance_report import PerformanceReportJob
from noc.sa.models.managedobject import ManagedObject
from noc.lib.serialize import json_decode


class DiscoveryDaemon(Daemon):
    daemon_name = "noc-discovery"

    def __init__(self, *args, **kwargs):
        self.beef = defaultdict(dict)  # method -> mo id -> beef
        super(DiscoveryDaemon, self).__init__(*args, **kwargs)
        self.scheduler = DiscoveryScheduler(self)
        self.install_beef()

    def run(self):
        try:
            PerformanceReportJob.submit(self.scheduler,
                key="performance_report", interval=60)
        except self.scheduler.JobExists:
            pass
        self.scheduler.run()

    def load_config(self):
        super(DiscoveryDaemon, self).load_config()
        self.load_beef_map()

    def load_beef_map(self):
        for o in self.config.options("beef"):
            method, mo_name = o.split(".", 1)
            try:
                mo = ManagedObject.objects.get(name=mo_name)
            except ManagedObject.DoesNotExist:
                logging.error("[beef] Unknown managed object: '%s'" % mo_name)
                continue
            beef = self.config.get("beef", o)
            logging.info("[%s] replacing object %s with beef %s" % (
                method, mo.name, beef
            ))
            self.beef[method][mo.id] = self.get_beef_result(
                beef)

    @classmethod
    def get_beef_result(cls, uuid):
        fn = "%s.json" % uuid
        for dirpath, dirs, files in os.walk("local/repos/sa/"):
            if fn in files:
                with open(os.path.join(dirpath, fn)) as f:
                    return json_decode(f.read())["result"]
        raise OSError("File not found: %s" % fn)

    def install_beef(self):
        for method in self.beef:
            self.scheduler.job_classes[method].set_beef(
                self.beef[method])

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
