# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.ESR.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus
from noc.core.text import parse_table


class Script(BaseScript):
    name = "Eltex.ESR.get_interface_status"
    interface = IGetInterfaceStatus

    def execute(self, interface=None):
        r = []
        c = self.cli("show interfaces status", cached=True)
        # ESR-12V ver.1.0.9 produce random empty lines
        c = "\n".join([s for s in c.split("\n") if s])
        for line in parse_table(c, allow_wrap=True):
            iface = line[0]
            lstate = line[2]
            if (interface is not None) and (interface != iface):
                continue
            r += [{"interface": iface, "status": lstate == "Up"}]
        return r
