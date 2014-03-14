## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IP Discovery Job
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import MODiscoveryJob
from noc.inv.discovery.reports.ipreport import IPReport
from noc.settings import config
from noc.inv.discovery.caches.vrf import vrf_cache


class IPDiscoveryJob(MODiscoveryJob):
    name = "ip_discovery"
    map_task = "get_ip_discovery"

    ignored = not config.getboolean("ip_discovery", "enabled")
    initial_submit_interval = config.getint("ip_discovery",
        "initial_submit_interval")
    initial_submit_concurrency = config.getint("ip_discovery",
        "initial_submit_concurrency")
    to_save = config.getboolean("ip_discovery", "save")

    def handler(self, object, result):
        """
        :param object:
        :param result:
        :return:
        """
        self.report = IPReport(self, to_save=self.to_save,
                               allow_prefix_restrictions=True)
        for v in result:
            vrf = vrf_cache.get_or_create(
                object, v["name"], v.get("rd", "0:0"))
            if vrf is None:
                self.info("Skipping unknown VRF '%s'" % v["name"])
                continue
            for a in v["addresses"]:
                self.report.submit(
                    vrf=vrf,
                    address=a["ip"],
                    interface=a["interface"],
                    mac=a["mac"])
        self.report.send()
        return True

    @classmethod
    def initial_submit_queryset(cls):
        return {"object_profile__enable_ip_discovery": True}

    def can_run(self):
        return (super(IPDiscoveryJob, self).can_run()
                and self.object.object_profile.enable_ip_discovery)

    @classmethod
    def get_submit_interval(cls, object):
        return object.object_profile.ip_discovery_max_interval

    def get_failed_interval(self):
        return self.object.object_profile.ip_discovery_min_interval
