# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QSW.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus


class Script(BaseScript):
    name = "Qtech.QSW2800.get_interface_status"
    interface = IGetInterfaceStatus
    cache = True

    rx_interface_status = re.compile(
        r"^\s*(?P<interface>\S+)\s+is\s+(?:administratively\s+)?\S+, "
        r"line protocol is (?P<status>\S+)",
        re.MULTILINE,
    )

    def execute_cli(self, interface=None):
        r = []
        if interface:
            cmd = "show interface %s" % interface
        else:
            cmd = "show interface | include line"
        for match in self.rx_interface_status.finditer(self.cli(cmd)):
            iface = match.group("interface")
            if iface.startswith("Vlan") or iface.startswith("l2over"):
                continue
            r += [{"interface": iface, "status": match.group("status").lower() == "up"}]
        return r
