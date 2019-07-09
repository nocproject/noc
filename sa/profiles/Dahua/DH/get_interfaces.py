# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Dahua.DH.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
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
                "mtu": res["table.Network.%s.MTU" % name],
                "mac": res["table.Network.%s.PhysicalAddress" % name],
            }
            ip_address = "%s/%s" % (
                res["table.Network.%s.IPAddress" % name],
                IPv4.netmask_to_len(res["table.Network.%s.SubnetMask" % name]),
            )

            sub = {
                "name": name,
                "admin_status": True,
                "oper_status": True,
                "mac": res["table.Network.%s.PhysicalAddress" % name],
                "enabled_afi": ["IPv4"],
                "ipv4_addresses": [ip_address],
            }
            iface["subinterfaces"] = [sub]
            r += [iface]

        return [{"interfaces": r}]
