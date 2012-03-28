# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOS.get_mpls_vpn
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
    name = "Juniper.JUNOS.get_mpls_vpn"
    implements = [IGetMPLSVPN]

    rx_ri = re.compile(r"(?P<name>\S+?):\n"
                       r"(?:  Description: (?P<description>.+?)\n)?"
                       r"  Router ID: \S+\n"
                       r"  Type: (?P<type>\S+)\s+\S*\s+State:\s+(?P<status>Active|Inactive)\s*\n"
                       r"  Interfaces:\n"
                       r"(?P<ifaces>(?:    \S+\n)*)"
                       r"  Route-distinguisher: (?P<rd>\S+)",
        re.MULTILINE | re.IGNORECASE
    )
    type_map = {
        "vrf": "VRF",
        "vpls": "VPLS",
        "l2vpn": "VLL"
    }
    def execute(self, **kwargs):
        vpns = []
        v = self.cli("show route instance detail")
        for match in self.rx_ri.finditer(v):
            name = match.group("name")
            rt = match.group("type").lower()
            if (name == "master" or name.startswith("__") or
                rt not in self.type_map):
                continue
            interfaces = [x.strip()
                          for x in match.group("ifaces").splitlines()]
            interfaces = [x for x in interfaces
                          if x and not x.startswith("lsi.")]
            vpn = {
                "type": self.type_map[rt],
                "status": match.group("status").lower() == "active",
                "name": name,
                "rd": match.group("rd"),
                "interfaces": interfaces
            }
            description = match.group("description")
            if description:
                vpn["description"] = description.strip()
            vpns += [vpn]
        return vpns
