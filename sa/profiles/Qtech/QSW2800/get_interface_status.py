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
from noc.sa.interfaces.igetinterfacestatusex import IGetInterfaceStatusEx


class Script(BaseScript):
    name = "Qtech.QSW2800.get_interface_status"
    interface = IGetInterfaceStatusEx
    cache = True

    rx_interface_status = re.compile(
        r"^\s*(?P<interface>\S+)\s+is\s+(?:administratively\s+)?"
        r"(?P<status>\S+), line protocol is \S+", re.MULTILINE)

    def execute(self, interface=None):
        r = []
        snmp = self.scripts.get_interface_status_ex()
        if snmp:
            return snmp
        if interface:
            cmd = "show interface %s" % interface
        else:
            cmd = "show interface | include line"
        for match in self.rx_interface_status.finditer(self.cli(cmd)):
            iface = match.group("interface")
            if iface.startswith("Vlan"):
                continue
            r.append({
                    "interface": iface,
                    "oper_status": match.group("status").lower() == "up"
            })
        return r
