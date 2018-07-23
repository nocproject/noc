# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QSW.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.sa.profiles.Generic.get_interface_status_ex import Script as BaseScript
from noc.sa.interfaces.igetinterfacestatusex import IGetInterfaceStatusEx


class Script(BaseScript):
    name = "Qtech.QSW2800.get_interface_status_ex"
    interface = IGetInterfaceStatusEx
    cache = True

    rx_interface_status = re.compile(
        r"^\s*(?P<interface>\S+)\s+is\s+(?:administratively\s+)?"
        r"(?P<admin_status>\S+), line protocol is (?P<oper_status>\S+)",
        re.MULTILINE
    )

    def execute_cli(self, interface=None):
        r = []
        if interface:
            cmd = "show interface %s" % interface
        else:
            cmd = "show interface | include line"
        for match in self.rx_interface_status.finditer(self.cli(cmd)):
            iface = match.group("interface")
            if (
                iface.startswith("Vlan") or iface.startswith("Loop") or
                iface.startswith("l2over")
            ):
                continue
            r += [{
                "interface": iface,
                "admin_status": match.group("admin_status").lower() == "up",
                "oper_status": match.group("oper_status").lower() == "up"
            }]
        return r
