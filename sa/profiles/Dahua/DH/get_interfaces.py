# ---------------------------------------------------------------------
# Dahua.DH.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "Dahua.DH.get_interfaces"
    cache = True
    interface = IGetInterfaces

    def execute(self):
        res = self.http.get("/cgi-bin/configManager.cgi?action=getConfig&name=Network")
        # "getInterfaces"
        r = []
        if res:
            res = self.profile.parse_equal_output(res)
            name = res["table.Network.DefaultInterface"]
            iface = {
                "name": name,
                "type": "physical",
                "admin_status": True,
                "oper_status": True,
                "hints": ["noc::interface::role::uplink"],
                "mtu": res[f"table.Network.{name}.MTU"],
                "mac": res[f"table.Network.{name}.PhysicalAddress"],
            }
            ip_address = "%s/%s" % (
                res[f"table.Network.{name}.IPAddress"],
                IPv4.netmask_to_len(res[f"table.Network.{name}.SubnetMask"]),
            )

            sub = {
                "name": name,
                "admin_status": True,
                "oper_status": True,
                "mac": res[f"table.Network.{name}.PhysicalAddress"],
                "enabled_afi": ["IPv4"],
                "ipv4_addresses": [ip_address],
            }
            iface["subinterfaces"] = [sub]
            r += [iface]

        return [{"interfaces": r}]
