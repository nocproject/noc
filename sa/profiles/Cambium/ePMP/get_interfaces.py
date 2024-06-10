# ---------------------------------------------------------------------
# Cambium.ePMP.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re
from collections import defaultdict

# NOC modules
from noc.core.ip import IPv4
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "Cambium.ePMP.get_interfaces"
    interface = IGetInterfaces

    INTERFACE_TYPES = {"ether": "physical", "/ieee802.11": "physical"}

    rx_iface = re.compile(
        r"\d+: (?P<name>\S+):\s<(?P<status>\S+)>\s[a-zA-Z0-9,<>_ \-]+\n"
        r"\s+link\/(?P<type>\S+)\s(?P<mac>\S+) brd.+\n"
        r"(\s+inet\s+(?P<inet_ip>\S+)/(?P<inet_prefix>\d+)\s+brd\s+"
        r"(?P<inet_broadcast>\S+)\s+scope\s+(?P<scope>\S+)\s+|)",
        re.MULTILINE,
    )

    def execute_cli(self):
        r = []
        subs = defaultdict(list)
        v = self.cli("show ip", cached=True).strip()

        for match in self.rx_iface.finditer(v):
            num = None
            iface_name = match.group("name").split("@")[0]
            i_type = self.INTERFACE_TYPES.get(match.group("type"), "other")
            s = {
                "name": iface_name,
                "admin_status": "LOWER_UP" in match.group("status"),
                "oper_status": "UP" in match.group("status"),
                "type": i_type,
                "mac": match.group("mac"),
                "enabled_protocols": [],
            }
            if "." in iface_name:
                iface_name, num = iface_name.rsplit(".", 1)
            if num:
                if int(num) < 4000:
                    s["vlan_ids"] = num
            if match.group("inet_ip"):
                s["ipv4_addresses"] = [IPv4(match.group("inet_ip"))]
                s["enabled_afi"] = ["IPv4"]
            subs[iface_name] += [s.copy()]

            # sub = {"subinterfaces": [i.copy()]}
            r += [
                {
                    "name": iface_name,
                    "admin_status": "LOWER_UP" in match.group("status"),
                    "oper_status": "UP" in match.group("status"),
                    "type": i_type,
                    "mac": match.group("mac"),
                    "enabled_protocols": [],
                }
            ]

        for l in r:
            if l["name"] in subs:
                l["subinterfaces"] = subs[l["name"]]
            else:
                l["subinterfaces"] = [
                    {
                        "name": l["name"],
                        "description": l.get("description", ""),
                        "type": "SVI",
                        "enabled_afi": (
                            ["BRIDGE"] if l["type"] in ["physical", "aggregated"] else []
                        ),
                        "admin_status": l["admin_status"],
                        "oper_status": l["oper_status"],
                        "snmp_ifindex": l["snmp_ifindex"],
                    }
                ]
        return [{"interfaces": r}]
