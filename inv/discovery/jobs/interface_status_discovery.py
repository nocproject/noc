## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Interface status discovery job
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import MODiscoveryJob
from noc.settings import config
from noc.inv.discovery.reports.interfacestatusreport import InterfaceStatusReport


class InterfaceStatusDiscovery(MODiscoveryJob):
    name = "interface_status_discovery"
    map_task = "get_interface_status_ex"

    ignored = not config.getboolean("interface_status_discovery", "enabled")
    to_save = config.getboolean("interface_status_discovery", "save")

    def handler(self, object, result):
        """
        :param object:
        :param result:
        :return:
        """
        self.report = InterfaceStatusReport(
            self, to_save=self.to_save
        )
        for i in result:
            self.report.submit(
                interface=i["interface"],
                admin_status=i.get("admin_status"),
                oper_status=i.get("oper_status"),
                full_duplex=i.get("full_duplex"),
                in_speed=i.get("in_speed"),
                out_speed=i.get("out_speed"),
                bandwidth=i.get("bandwidth")
            )
        self.report.send()
        return True

    def can_run(self):
        return (super(InterfaceStatusDiscovery, self).can_run()
                and self.object.object_profile.enable_interface_status_discovery)

    def get_failed_interval(self):
        return self.object.object_profile.interface_status_discovery_min_interval
