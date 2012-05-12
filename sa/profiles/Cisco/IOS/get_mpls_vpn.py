# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_mpls_vpn
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetMPLSVPN


class Script(NOCScript):
    name = "Cisco.IOS.get_mpls_vpn"
    implements = [IGetMPLSVPN]

    rx_line = re.compile(r"^\s+(?P<vrf>.+?)\s+"
                         r"(?P<rd>\S+:\S+|<not set>)\s+"
                         "(?P<iface>.*?)\s*$", re.IGNORECASE)
    rx_cont = re.compile("^\s{6,}(?P<iface>.+?)\s*$")

    def execute(self, **kwargs):
        vpns = []
        v = self.cli("show ip vrf")
        for l in v.splitlines():
            match = self.rx_line.match(l)
            if match:
                iface = match.group("iface").strip()
                if iface:
                    interfaces = [iface]
                else:
                    interfaces = []
                vpn = {
                    "type": "VRF",
                    "status": True,
                    "name": match.group("vrf"),
                    "interfaces": interfaces
                }
                rd = match.group("rd")
                if ":" in rd:
                    vpn["rd"] = rd
                vpns += [vpn]
            elif vpns:
                match = self.rx_cont.match(l)
                if match:
                    vpns[-1]["interfaces"] += [match.group("iface")]
        return vpns
