# ----------------------------------------------------------------------
# GWD.GFA.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "GWD.GFA.get_interfaces"
    interface = IGetInterfaces

    rx_iface = re.compile(
        r"^Interface (?:eth|pon)(?P<name>\d+/\d+) is (?P<oper_status>up|down)\.\s*\n"
        r"^\s+Physical status is \S+, administrator status is (?P<admin_status>up|down)\.\s*\n"
        r"^\s+Interface description: (?P<description>.+)\n"
        r"^\s+MTU (?P<mtu>\d+) bytes\.\s*\n",
        re.MULTILINE,
    )
    rx_vlan = re.compile(
        r"^Interface VLAN (?P<name>\S+) is (?P<oper_status>up|down)\.\s*\n"
        r"^\s+Physical status is \S+, administrator status is (?P<admin_status>up|down)\.\s*\n"
        r"(^\s+Interface description: (?P<description>.+?)\s*\n)?"
        r"^\s+MTU (?P<mtu>\d+) bytes\.\s*\n"
        r"(^\s+IP address:\s*\n)?"
        r"(^\s+(?P<ip>\d+\S+)\s*\n)?"
        r"^\s+IP binding \S+\.\s*\n"
        r"^\s+MulitiCast Flood Mode is \d+\.\s*\n"
        r"^\s+Vlan id is (?P<vlan_id>\d+)\.\s*\n"
        r"^\s+Port member list:\s*\n"
        r"(?P<ports>(.+\n)*)"
        r"^\s+Trunk member list:",
        re.MULTILINE,
    )
    rx_loop = re.compile(
        r"^Interface loopback (?P<name>\S+) is (?P<oper_status>up|down)\.\s*\n"
        r"^\s+Physical status is \S+, administrator status is (?P<admin_status>up|down)\.\s*\n"
        r"(^\s+Interface description: (?P<description>.+?)\s*\n)?"
        r"^\s+MTU (?P<mtu>\d+) bytes\.\s*\n"
        r"(^\s+IP address:\s*\n)?"
        r"(^\s+(?P<ip>\d+\S+)\s*\n)?"
        r"^\s+IP binding \S+\.\s*\n",
        re.MULTILINE,
    )

    rx_port = re.compile(r"(?:eth|pon)(?P<port>\d+/\d+)\((?P<mode>u|t)\)")
    rx_mac = re.compile(
        r"^\*(?P<mac>\S+)\s+(?P<vlan>\S+)\s+(?P<port>CPU)\s+Static\s*\n", re.MULTILINE
    )

    def execute_cli(self):
        interfaces = []
        v = self.cli("show interface ethernet")
        for match in self.rx_iface.finditer(v):
            iface = {
                "name": match.group("name"),
                "type": "physical",
                "admin_status": match.group("admin_status") == "UP",
                "oper_status": match.group("oper_status") == "UP",
                "description": match.group("description").strip(),
                "subinterfaces": [
                    {
                        "name": match.group("name"),
                        "admin_status": match.group("admin_status") == "UP",
                        "oper_status": match.group("oper_status") == "UP",
                        "description": match.group("description").strip(),
                        "mtu": match.group("mtu"),
                    }
                ],
            }
            interfaces += [iface]
        v = self.cli("show interface vlan")
        for match in self.rx_vlan.finditer(v):
            iface = {
                "name": match.group("name"),
                "type": "SVI",
                "admin_status": match.group("admin_status") == "UP",
                "oper_status": match.group("oper_status") == "UP",
            }
            sub = {
                "name": match.group("name"),
                "admin_status": match.group("admin_status") == "UP",
                "oper_status": match.group("oper_status") == "UP",
                "mtu": match.group("mtu"),
                "vlan_ids": [match.group("vlan_id")],
            }
            if match.group("description"):
                iface["description"] = match.group("description")
                sub["description"] = match.group("description")
            if match.group("ip"):
                sub["enabled_afi"] = ["IPv4"]
                sub["ipv4_addresses"] = [match.group("ip")]
            iface["subinterfaces"] = [sub]
            interfaces += [iface]
            for match1 in self.rx_port.finditer(match.group("ports")):
                port = match1.group("port")
                mode = match1.group("mode")
                for i in interfaces:
                    if i["name"] == port:
                        sub = i["subinterfaces"][0]
                        if mode == "u":
                            sub["untagged_vlan"] = match.group("vlan_id")
                        elif "tagged_vlans" in sub:
                            sub["tagged_vlans"] += [match.group("vlan_id")]
                        else:
                            sub["tagged_vlans"] = [match.group("vlan_id")]
                        break
        v = self.cli("show forward-entry", cached=True)
        for match in self.rx_mac.finditer(v):
            iface = match.group("vlan")
            for i in interfaces:
                if i["name"] == iface:
                    i["mac"] = match.group("mac")
                    i["subinterfaces"][0]["mac"] = match.group("mac")
                    break
        v = self.cli("show interface loopback")
        for match in self.rx_loop.finditer(v):
            iface = {
                "name": match.group("name"),
                "type": "loopback",
                "admin_status": match.group("admin_status") == "UP",
                "oper_status": match.group("oper_status") == "UP",
            }
            sub = {
                "name": match.group("name"),
                "admin_status": match.group("admin_status") == "UP",
                "oper_status": match.group("oper_status") == "UP",
                "mtu": match.group("mtu"),
            }
            if match.group("description"):
                iface["description"] = match.group("description")
                sub["description"] = match.group("description")
            if match.group("ip"):
                sub["enabled_afi"] = ["IPv4"]
                sub["ipv4_addresses"] = [match.group("ip")]
            iface["subinterfaces"] = [sub]
            interfaces += [iface]

        return [{"interfaces": interfaces}]
