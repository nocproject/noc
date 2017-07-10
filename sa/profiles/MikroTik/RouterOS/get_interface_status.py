# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MikroTik.RouterOS.get_interface_status"
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus


class Script(BaseScript):
    name = "MikroTik.RouterOS.get_interface_status"
    interface = IGetInterfaceStatus

    def execute(self, interface=None):
        ifaces = []
        # Fill interfaces
        for n, f, r in self.cli_detail(
        "/interface print detail without-paging"):
            iface = {"interface": r["name"], "status": "R" in f}
            if (interface is not None) and (interface == r["name"]):
                return [iface]
            ifaces += [iface]
        return ifaces
