# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Interface Status check
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.inv.models.interface import Interface


class InterfaceStatusCheck(DiscoveryCheck):
    """
    Interface status discovery
    """
    name = "interfacestatus"
    required_script = "get_interface_status_ex"

    def handler(self):
        has_interfaces = "DB | Interfaces" in self.object.get_caps()
        if not has_interfaces:
            self.logger.info(
                "No interfaces discovered. "
                "Skipping interface status check"
            )
            return
        self.logger.info(
            "Checking interface statuses"
        )
        result = self.object.scripts.get_interface_status_ex()
        interfaces = dict(
            (i.name, i)
            for i in Interface.objects.filter(
                managed_object=self.object.id)
        )
        for i in result:
            iface = interfaces.get(i["interface"])
            if not iface:
                continue
            kwargs = {
                "name": i["interface"],
                "admin_status": i.get("admin_status"),
                "full_duplex": i.get("full_duplex"),
                "in_speed": i.get("in_speed"),
                "out_speed": i.get("out_speed"),
                "bandwidth": i.get("bandwidth")
            }
            changes = self.update_if_changed(
                iface, kwargs,
                ignore_empty=kwargs.keys(),
                async=True
            )
            self.log_changes(
                "Interface %s status has been changed" % i["interface"],
                changes
            )
            ostatus = i.get("oper_status")
            if iface.oper_status != ostatus and ostatus is not None:
                self.logger.info("[%s] set oper status to %s",
                                 i["interface"], ostatus)
                iface.set_oper_status(ostatus)
