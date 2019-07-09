# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DVG.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus


class Script(BaseScript):
    name = "DLink.DVG.get_interface_status"
    interface = IGetInterfaceStatus

    def execute_snmp(self, **kwargs):
        r = []
        # Only one way: SNMP.
        for i, n, s in self.snmp.join(["1.3.6.1.2.1.2.2.1.2", "1.3.6.1.2.1.2.2.1.8"]):
            if n[:3] == "eth" or n[:3] == "gre":
                r += [{"interface": n, "status": int(s) == 1}]
        return r
