# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Siklu.EH.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "Siklu.EH.get_interfaces"
    cache = True
    interface = IGetInterfaces

    rx_ecfg = re.compile(
        r"^(?P<cmd>\S+)\s+(?P<name>\S+)\s+(?P<key>\S+)\s*:\s*(?P<value>.*?)$",
        re.MULTILINE
    )

    def parse_section(self, section):
        r = {}
        name = None
        for match in self.rx_ecfg.finditer(section):
            name = match.group("name")
            r[match.group("key")] = match.group("value").strip()
        return name, r

    def execute(self):
        v = self.cli("show eth all")
        ifaces = []
        for section in v.split("\n\n"):
            if not section:
                continue
            name, cfg = self.parse_section(section)
            i = {
                "name": name,
                "type": "physical",
                "mac": cfg["mac-addr"],
                "description": cfg["description"],
                "admin_status": cfg["admin"] == "up",
                "oper_status": cfg["operational"] == "up",
                "subinterfaces": []
            }
            ifaces += [i]
        # @todo: show ip all
        # @todo: show vlan
        return [{"interfaces": ifaces}]
