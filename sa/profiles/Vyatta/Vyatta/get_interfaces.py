# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vyatta.Vyatta.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
from collections import defaultdict
# NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(NOCScript):
    """
    Vyatta.Vyatta.get_interfaces
    """
    name = "Vyatta.Vyatta.get_interfaces"
    implements = [IGetInterfaces]

    rx_int = re.compile(r"^(?P<name>.+?):\s+<.+?> mtu \d+ .+state")
    rx_descr = re.compile(r"^\s+Description:\s+(?P<descr>.+?)\s*$")
    rx_inet = re.compile(r"^\s+inet\s+(?P<inet>\S+)")
    rx_inet6 = re.compile(r"^\s+inet6\s+(?P<inet6>\S+)")

    def execute(self):
        ifaces = {}
        last_if = None
        il = []
        subs = defaultdict(list)
        for l in self.cli("show interfaces detail").splitlines():
            # New interface
            match = self.rx_int.search(l)
            if match:
                last_if = match.group("name")
                il += [last_if]  # preserve order
                ifaces[last_if] = {
                    "name": last_if,
                    "ipv4_addresses": [],
                    "ipv6_addresses": [],
                    "admin_status": True,
                    "oper_status": True,
                    "enabled_afi": []
                }
                if "@" in last_if:
                    name, base = last_if.split("@")
                    subs[base] += [last_if]
                    ifaces[last_if]["vlan_ids"] = [int(name.split(".")[-1])]
                    ifaces[last_if]["name"] = name
                continue
            # Description
            match = self.rx_descr.search(l)
            if match:
                ifaces[last_if]["description"] = match.group("descr")
                continue
            # inet
            match = self.rx_inet.search(l)
            if match:
                ifaces[last_if]["ipv4_addresses"] += [match.group("inet")]
                continue
            # inet6
            match = self.rx_inet6.search(l)
            if match:
                ifaces[last_if]["ipv6_addresses"] += [match.group("inet6")]
                continue
        # Process interfaces
        r = []
        for iface in il:
            if iface in subs:
                i = {
                    "name": iface.split(".")[0],
                    "type": self.profile.get_interface_type(iface),
                    "admin_status": True,
                    "oper_status": True,
                    "subinterfaces": [self.get_si(ifaces[si])
                                      for si in subs[iface]]
                }
                if ifaces[iface].get("description"):
                    i["description"] = ifaces["iface"]["description"]
            elif "@" not in iface:
                i = {
                    "name": iface.split(".")[0],
                    "type": self.profile.get_interface_type(iface),
                    "admin_status": True,
                    "oper_status": True,
                    "subinterfaces": [self.get_si(ifaces[iface])]
                }
                if ifaces[iface].get("description"):
                    i["description"] = ifaces["iface"]["description"]
            else:
                continue  # Already processed
            r += [i]
        return [{"interfaces": r}]

    def get_si(self, si):
        if si["ipv4_addresses"]:
            si["ipv4_addresses"] = list(si["ipv4_addresses"])
            si["enabled_afi"] += ["IPv4"]
        else:
            del si["ipv4_addresses"]
        if si["ipv6_addresses"]:
            si["ipv6_addresses"] = list(si["ipv6_addresses"])
            si["enabled_afi"] += ["IPv6"]
        else:
            del si["ipv6_addresses"]
        return si
