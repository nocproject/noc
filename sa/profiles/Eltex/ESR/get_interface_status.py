# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.ESR.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.lib.text import parse_table
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus


class Script(BaseScript):
    name = "Eltex.ESR.get_interface_status"
    interface = IGetInterfaceStatus

    def execute(self, interface=None):
        r = []
        c = self.cli("show interfaces status", cached=True)
        for iface, astate, lstate, mtu, mac in parse_table(c):
            if (interface is not None) and (interface != iface):
                continue
            r += [{
                "interface": iface,
                "status": lstate == "Up"
            }]
        return r
