# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Planet.WGSD.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "Planet.WGSD.get_arp"
    interface = IGetARP
    cache = True

    rx_line = re.compile(
        r"^vlan\s+(?P<interface>\d+)\s+(?P<ip>\S+)\s+(?P<mac>\S+)\s+(dynamic|static)\s*$",
        re.MULTILINE)

    def execute_snmp(self):
        r = []
        for v in self.snmp.get_tables(["1.3.6.1.2.1.4.22.1.1",
                                       "1.3.6.1.2.1.4.22.1.2",
                                       "1.3.6.1.2.1.4.22.1.3"], bulk=True):
            iface = self.snmp.get("1.3.6.1.2.1.31.1.1.1.1.%s" % int(v[1]), cached=True)  # Vlan ID, not interface name!
            mac = ":".join(["%02x" % ord(c) for c in v[2]])
            r.append({"ip": v[3],
                      "mac": mac,
                      "interface": iface,
                      })
        return r

    def execute_cli(self):
        r = []
        # Fallback to CLI
        for match in self.rx_line.finditer(self.cli("show arp", cached=True)):
            mac = match.group("mac")
            if mac.lower() == "incomplete":
                r.append({
                    "ip": match.group("ip"),
                    "mac": None,
                    "interface": None
                })
            else:
                r.append({
                    "ip": match.group("ip"),
                    "mac": match.group("mac"),
                    "interface": match.group("interface")
                })
        return r
