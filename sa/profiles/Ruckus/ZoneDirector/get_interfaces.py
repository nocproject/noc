# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Ruckus.ZoneDirector.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "Ruckus.ZoneDirector.get_interfaces"
    interface = IGetInterfaces

    rx_iface = re.compile(
        r"\s*Interface=\s+(?P<name>\S+)+\n"
        r"\s*MAC\sAddress=\s+(?P<mac>\S+)+\n"
        r"\s*Physical\sLink=\s+(?P<admin_status>up|down)+\n",
        re.MULTILINE | re.DOTALL
    )

    def execute(self, interface=None):
        interfaces = []
        # Ethernet ports
        v = self.cli("show ethinfo")
        for match in self.rx_iface.finditer(v):
            interfaces += [{
                "name": match.group("name"),
                "type": "physical",
                "mac": match.group("mac"),
                "admin_status": match.group("admin_status").lower() == "up",
                "subinterfaces": [{
                    "name": match.group("name"),
                    "mac": match.group("mac"),
                    "admin_status": match.group("admin_status").lower() == "up",
                    "enabled_afi": ["BRIDGE"]
                }]
            }]
        return [{"interfaces": interfaces}]
