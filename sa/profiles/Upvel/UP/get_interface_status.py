# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Upvel.UP.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus
from noc.core.text import parse_table


class Script(BaseScript):
    name = "Upvel.UP.get_interface_status"
    interface = IGetInterfaceStatus

    def execute_cli(self, interface=None):
        r = []
        v = self.cli("show interface * status", cached=True)
        for i in parse_table(v):
            ifname = i[0]
            status = i[6] != "Down"
            if (interface is not None) and (interface == ifname):
                return [{"interface": ifname, "status": status}]
            r += [{"interface": ifname, "status": status}]
        return r
