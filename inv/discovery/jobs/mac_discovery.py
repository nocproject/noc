## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IP Discovery Job
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import MODiscoveryJob
from noc.inv.discovery.reports.macreport import MACReport
from noc.settings import config
from noc.inv.models.subinterface import SubInterface


class MACDiscoveryJob(MODiscoveryJob):
    name = "mac_discovery"
    map_task = "get_mac_address_table"

    ignored = not config.getboolean("mac_discovery", "enabled")
    initial_submit_interval = config.getint("mac_discovery",
        "initial_submit_interval")
    initial_submit_concurrency = config.getint("mac_discovery",
        "initial_submit_concurrency")
    success_retry = config.getint("mac_discovery", "success_retry")
    failed_retry = config.getint("mac_discovery", "failed_retry")
    to_save = config.getboolean("mac_discovery", "save")

    def handler(self, object, result):
        """
        :param object:
        :param result:
        :return:
        """
        self.report = MACReport(self, to_save=self.to_save)
        for v in result:
            if v["type"] == "D" and v["interfaces"]:
                self.report.submit(
                    mac=v["mac"],
                    vlan=v["vlan_id"],
                    managed_object=object,
                    if_name=v["interfaces"][0]
                )
        self.report.send()
        return True

    @classmethod
    def can_submit(cls, object):
        """
        Check object has bridge interfaces
        :param cls:
        :param object:
        :return:
        """
        return bool(SubInterface.objects.filter(
            managed_object=object.id, enabled_afi="BRIDGE").first())
