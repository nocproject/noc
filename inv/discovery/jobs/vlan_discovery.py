## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## VLAN Discovery Job
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import MODiscoveryJob
from noc.inv.discovery.reports.vlanreport import VLANReport
from noc.settings import config
from noc.inv.discovery.caches.vrf import vrf_cache


class VLANDiscoveryJob(MODiscoveryJob):
    name = "vlan_discovery"
    map_task = "get_vlans"

    ignored = not config.getboolean("vlan_discovery", "enabled")
    to_save = config.getboolean("vlan_discovery", "save")

    def handler(self, object, result):
        """
        :param object:
        :param result:
        :return:
        """
        vc_domain = object.vc_domain
        self.report = VLANReport(self, to_save=self.to_save)
        for v in result:
            self.report.submit(
                vc_domain=vc_domain,
                l1=v["vlan_id"],
                name=v.get("name")
            )
        self.report.send()
        return True

    def can_run(self):
        return (
            super(VLANDiscoveryJob, self).can_run() and
            self.object.object_profile.enable_vlan_discovery and
            self.object.vc_domain
        )

    def get_failed_interval(self):
        return self.object.object_profile.vlan_discovery_min_interval
