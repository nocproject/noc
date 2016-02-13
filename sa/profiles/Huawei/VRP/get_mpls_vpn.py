# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP.get_mpls_vpn
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmplsvpn import IGetMPLSVPN


class Script(BaseScript):
    name = "Huawei.VRP.get_mpls_vpn"
    interface = IGetMPLSVPN

    rx_line = re.compile(r"^\s+VPN\-Instance Name and ID :\s+(?P<vrf>\S+?),", re.IGNORECASE)
    rx_rd = re.compile(r"^\s+Route Distinguisher :\s+(?P<rd>\S+:\S+|<not set>)\s*", re.IGNORECASE)
    rx_int = re.compile(r"^(?:\s{,4}Interfaces :\s+|\s{6,})(?P<iface>.+?),?\s*$", re.IGNORECASE)
    rx_desc = re.compile(r"^\s+Description :\s+(?P<desc>.*)\s*", re.IGNORECASE)

    def execute(self, **kwargs):
        vpns = []
        try:
            v = self.cli("display ip vpn-instance verbose")
        except self.CLISyntaxError:
            return []
        for l in v.splitlines():
            match = self.rx_line.search(l)
            if match:
                vpns += [{
                    "type": "VRF",
                    "status": True,
                    "name": match.group("vrf").strip(),
                    "interfaces": []
                }]
            elif vpns:
                match_rd = self.rx_rd.match(l)
                if match_rd:
                    rd = match_rd.group("rd")
                    if ":" in rd:
                        vpns[-1]["rd"] = rd
                    continue

                match_int = self.rx_int.match(l)
                if match_int:
                    vpns[-1]["interfaces"] += [match_int.group("iface")]
                    continue

                match_desc = self.rx_desc.match(l)
                if match_desc:
                    vpns[-1]["description"] = match_desc.group("desc").strip()
                    continue
        return vpns
