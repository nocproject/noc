# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# UTST.ONU.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "UTST.ONU.get_interfaces"
    cache = True
    interface = IGetInterfaces

    rx_int1 = re.compile(
        r"(?P<ifname>lan[0-9]|ge|uplink)",
        re.MULTILINE)

    rx_int2 = re.compile(
        r"^(?P<ifname>\d+):\s+(?P<admin_status>\S+)\s+(?P<oper_status>\S+)?",
        re.MULTILINE)

    def execute(self):
        interfaces = []
        v = self.cli("show port")
        if (self.match_version(version__contains="2.0.3.6")):
            for match in self.rx_int1.finditer(v):
                ifname = match.group("ifname")
                iface = {
                    "name": ifname,
                    "type": "physical",
                    "admin_status": True,
                    "oper_status": True,
                    "subinterfaces": [{
                        "name": ifname,
                        "admin_status": True,
                        "oper_status": True,
                        "enabled_afi": ["BRIDGE"]
                    }]
                }
                interfaces += [iface]
        else:
            for match in self.rx_int2.finditer(v):
                ifname = match.group("ifname")
                if "on" in match.group("admin_status"):
                    admin_status = True
                else:
                    admin_status = False
                if "up" in match.group("oper_status"):
                    oper_status = True
                else:
                    oper_status = False
                iface = {
                    "name": ifname,
                    "type": "physical",
                    "admin_status": admin_status,
                    "oper_status": oper_status,
                    "subinterfaces": [{
                        "name": ifname,
                        "admin_status": admin_status,
                        "oper_status": oper_status,
                        "enabled_afi": ["BRIDGE"]
                    }]
                }
                interfaces += [iface]
        return [{"interfaces": interfaces}]
