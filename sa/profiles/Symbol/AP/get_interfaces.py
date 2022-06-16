# ---------------------------------------------------------------------
# Symbol.AP.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "Symbol.AP.get_interfaces"
    interface = IGetInterfaces

    rx_iface = re.compile(
        r"^Interface (?P<ifname>\S+) is (?P<oper_status>UP|DOWN)\s*\n"
        r"^\s+Hardware-type: (?:ethernet|vlan), Mode: Layer (?:2|3), Address: (?P<mac>\S+)\s*\n"
        r"^\s+Index: (?P<snmp_ifindex>\d+), Metric: \d+, MTU: (?P<mtu>\d+)\s*\n"
        r"(^\s+(?:ip a|IP-A)ddress:? (?P<ip>\d\S+\d))?",
        re.MULTILINE,
    )
    rx_wlan_config = re.compile(
        r"^\s+(?P<name>\S+)\s+Y\s+(?P<ssid>\S+)\s+\S+\s+\S+\s+(?P<vlan_id>\d+)\s+\S+\s*\n",
        re.MULTILINE,
    )
    rx_wlan = re.compile(
        r"^Radio: (?P<mac>\S+):(?P<sub_name>\S+),.+\n"
        r"^\s+STATE\s+: (?P<oper_status>Off|On).*\n"
        r"^\s+PHY INFO\s+: Bssid: (?P<sub_mac>\S+) RF-Mode:",
        re.MULTILINE,
    )
    rx_switchport = re.compile(
        r"^\s+(?P<ifname>ge\d+)\s+(?:UP|DOWN)\s+(?P<mode>access|trunk)\s+(?P<vlans>\S+)",
        re.MULTILINE,
    )
    rx_native = re.compile(r"(\d+)\*")

    def execute_cli(self):
        interfaces = []
        c = self.cli("show interface")
        for match in self.rx_iface.finditer(c):
            ifname = match.group("ifname")
            iface = {
                "name": ifname,
                "type": self.profile.get_interface_type(ifname),
                "admin_status": True,
                "oper_status": match.group("oper_status") == "UP",
                "mac": match.group("mac"),
                "snmp_ifindex": int(match.group("snmp_ifindex")),
                "subinterfaces": [
                    {
                        "name": ifname,
                        "admin_status": True,
                        "oper_status": match.group("oper_status") == "UP",
                        "mac": match.group("mac"),
                        "mtu": int(match.group("mtu")),
                    }
                ],
            }
            if ifname.startswith("ge"):
                iface["subinterfaces"][0]["enabled_afi"] = ["BRIDGE"]
            if ifname.startswith("vl"):
                iface["subinterfaces"][0]["vlan_ids"] = int(ifname[4:])
                if match.group("ip"):
                    iface["subinterfaces"][0]["enabled_afi"] = ["IPv4"]
                    iface["subinterfaces"][0]["ipv4_addresses"] = [match.group("ip")]
            interfaces += [iface]

        c = self.cli("show interface switchport")
        for match in self.rx_switchport.finditer(c):
            ifname = match.group("ifname")
            vlans = match.group("vlans")
            for iface in interfaces:
                if ifname == iface["name"]:
                    if match.group("mode") == "access":
                        iface["subinterfaces"][0]["untagged_vlan"] = int(vlans)
                    else:
                        if "*" in vlans:
                            untagged = int(self.rx_native.search(vlans).group(1))
                            iface["subinterfaces"][0]["untagged_vlan"] = untagged
                            vlans = vlans.replace("*", "")
                            tagged = self.expand_rangelist(vlans)
                            tagged.remove(int(untagged))
                        else:
                            tagged = self.expand_rangelist(vlans)
                        iface["subinterfaces"][0]["tagged_vlans"] = tagged
                    break
        c = self.cli("show wireless wlan config")
        vlans = []
        for match in self.rx_wlan_config.finditer(c):
            vlans += [int(match.group("vlan_id"))]
        c = self.cli("show wireless radio detail")
        iface = {"subinterfaces": []}
        for match in self.rx_wlan.finditer(c):
            iface["name"] = "WLAN"
            iface["type"] = "physical"
            iface["oper_status"] = True
            iface["mac"] = match.group("mac")
            iface["subinterfaces"] += [
                {
                    "name": match.group("sub_name").replace("R", "radio"),
                    "admin_status": match.group("oper_status") == "On",
                    "oper_status": match.group("oper_status") == "On",
                    "mac": match.group("sub_mac"),
                    "enabled_afi": ["BRIDGE"],
                    "tagged_vlans": vlans,
                }
            ]
        interfaces += [iface]
        return [{"interfaces": interfaces}]
