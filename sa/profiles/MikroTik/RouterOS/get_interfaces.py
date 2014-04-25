# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MikroTik.RouterOS.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaces


class Script(NOCScript):
    name = "MikroTik.RouterOS.get_interfaces"
    implements = [IGetInterfaces]

    type_map = {
        "ether": "physical",
        "wlan": "physical",
        "bridge": "SVI",
        "vlan": "SVI"
    }

    def execute(self):
        ifaces = {}
        # Fill interfaces
        for n, f, r in self.cli_detail("/interface print detail"):
            ifaces[r["name"]] = {
                "name": r["name"],
                "type": self.type_map[r["type"]],
                "admin_status": "X" not in f,
                "oper_status": "R" in f,
                "subinterfaces": []
            }
        # Refine ethernet parameters
        for n, f, r in self.cli_detail("/interface ethernet print detail"):
            ifaces[r["name"]]["mac"] = r["mac-address"]
        # Refine ip addresses
        for n, f, r in self.cli_detail("/ip address print detail"):
            i = ifaces[r["interface"]]
            afi = "IPv6" if ":" in r["address"] else "IPv4"
            if not i["subinterfaces"]:
                si = {
                    "name": r["interface"],
                    "enabled_afi": [afi],
                }
                if i.get("mac"):
                    si["mac"] = i["mac"]
                i["subinterfaces"] += [si]
            else:
                si = i["subinterfaces"][-1]
            if afi not in si["enabled_afi"]:
                si["enabled_afi"] += [afi]
            if afi == "IPv4":
                a = si.get("ipv4_addresses", [])
                a += [r["address"]]
                si["ipv4_addresses"] = a
            else:
                a = si.get("ipv6_addresses", [])
                a += [r["address"]]
                si["ipv6_addresses"] = a
        return [{"interfaces": ifaces.values()}]
