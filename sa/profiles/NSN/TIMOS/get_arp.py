# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# NSN.TIMOS.get_arp
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP
import re


class Script(BaseScript):
    name = "NSN.TIMOS.get_arp"
    interface = IGetARP
    rx_line = re.compile(
        r"^(?P<ip>\d+\.\d+\.\d+\.\d+)\s+(?P<mac>\S+)\s+\d+\S+\s+\S+\s+(?P<iface>.+)$"
    )
    rx_vrfs = re.compile(r"^(\d+)\s+VPRN\s+Up\s+Up", re.MULTILINE)

    def execute_cli(self, vrf=None):
        if vrf:
            s = self.cli("show router %s arp" % vrf)
        else:
            s = self.cli("show service service-using vprn")
            vrfs = self.rx_vrfs.findall(s)
            s = self.cli("show router arp")
            for vrf in vrfs:
                s += self.cli("show router %s arp" % vrf)
        r = []
        for l in s.split("\n"):
            match = self.rx_line.match(l.strip())
            if not match:
                continue
            mac = match.group("mac")
            if mac == "":
                r.append({"ip": match.group("ip"), "mac": None, "interface": None})
            else:
                r.append(
                    {
                        "ip": match.group("ip"),
                        "mac": match.group("mac"),
                        "interface": match.group("iface"),
                    }
                )
        return r
