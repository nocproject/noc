# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Rotek.RTBSv1.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Rotek.RTBSv1.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_iface = re.compile("^\s*WAN:\s+(?P<ifname>br\d+)", re.MULTILINE)
    rx_mac = re.compile("^\s*br\d+ mac:\s+(?P<mac>\S+)", re.MULTILINE)

    def execute_snmp(self):
        base = self.snmp.get("1.3.6.1.2.1.2.2.1.6.2")
        return [{
            "first_chassis_mac": base,
            "last_chassis_mac": base
        }]

    def execute_cli(self):
        c = self.cli("show interface list")
        match = self.rx_iface.search(c)
        ifname = match.group("ifname")
        c = self.cli("show interface %s mac" % ifname)
        match = self.rx_mac.search(c)
        return [{
            "first_chassis_mac": match.group("mac"),
            "last_chassis_mac": match.group("mac")
        }]
