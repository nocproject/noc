# ----------------------------------------------------------------------
# Mellanox.Cumulus.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.text import parse_table
from noc.core.validators import is_ipv4_prefix, is_ipv6_prefix


class Script(BaseScript):
    name = "Mellanox.Cumulus.get_interfaces"
    interface = IGetInterfaces

    rx_vrf = re.compile(r"^(?P<vrf>\S+)\s+\d+\s*\n", re.MULTILINE)
    rx_iface = re.compile(
        r"^\s+Interface (?P<ifname>\S+) is (?P<admin_status>up|down)(?:, line protocol is (?P<oper_status>up|down))?\s*\n"
        r"^\s+Link ups:.+\n"
        r"^\s+Link downs:.+\n"
        r"^\s+PTM status:.+\n"
        r"^\s+vrf: (?P<vrf>\S+)\s*\n"
        r"^\s+index (?P<snmp_ifindex>\d+) metric \d+ mtu (?P<mtu>\d+) speed \d+\s*\n"
        r"^\s+flags: .+\n"
        r"^\s+Type: .+\n"
        r"(?:^\s+HWaddr: (?P<mac>\S+))?",
        re.MULTILINE,
    )
    rx_ip = re.compile(r"^IP:\s+(?P<ip>[1-9:]\S+\d)\s*\n", re.MULTILINE)
    rx_vlan_id = re.compile(r"^\s+VLAN Id (?P<vlan_id>\d+)\s*\n", re.MULTILINE)
    rx_vlans = re.compile(
        r"^All VLANs on L2 Port\s*\n^--------------------\s*\n^(?P<vlans>\d\S+)\s*\n",
        re.MULTILINE,
    )
    rx_untagged = re.compile(r"^Untagged\s*\n^--------\s*\n^(?P<untagged>\d+)\s*\n", re.MULTILINE)

    INTERFACE_TYPES = {
        "Loopback": "loopback",
        "Mgmt": "management",
        "Trunk/L2": "physical",
        "NotConfigured": "physical",
        "Bridge/L2": "SVI",
        "SubInt/L3": "other",
        "Interface/L3": "SVI",
        "VRF": "other",
        "802.3ad": "aggregated",
    }

    def execute_cli(self):
        vrfs = [
            {
                "forwarding_instance": "default",
                "type": "table",
                "interfaces": [],
            }
        ]
        v = self.cli("net show vrf")
        for match in self.rx_vrf.finditer(v):
            vrfs += [
                {
                    "forwarding_instance": match.group("vrf"),
                    "type": "VRF",
                    "interfaces": [],
                }
            ]
        bridge_name = "bridge"  # default value
        v = self.cli("net show interface all")
        for line in parse_table(v):
            if not line[0]:
                continue
            ifname = line[1]
            iftype = line[4]
            if iftype == "VRF":
                continue
            c = self.cli(f"net show interface {ifname} detail")
            if "Interface Type VRF" in c:
                continue
            match = self.rx_iface.search(c)
            if match.group("oper_status"):
                oper_status = match.group("oper_status") == "up"
            else:
                oper_status = False
            iface = {
                "name": match.group("ifname"),
                "type": self.INTERFACE_TYPES.get(iftype, "unknown"),
                "admin_status": match.group("admin_status") == "up",
                "oper_status": oper_status,
                "snmp_ifindex": match.group("snmp_ifindex"),
                "subinterfaces": [],
            }
            sub = {
                "name": match.group("ifname"),
                "admin_status": match.group("admin_status") == "Enabled",
                "oper_status": oper_status,
                "mtu": match.group("mtu"),
                "snmp_ifindex": match.group("snmp_ifindex"),
            }
            if match.group("mac"):
                iface["mac"] = match.group("mac")
                sub["mac"] = match.group("mac")
            if iface["type"] == "physical":
                sub["enabled_afi"] = ["BRIDGE"]
            for match1 in self.rx_ip.finditer(c):
                ip = match1.group("ip")
                if is_ipv4_prefix(ip):
                    if "enabled_afi" in sub:
                        sub["enabled_afi"] += ["IPv4"]
                    else:
                        sub["enabled_afi"] = ["IPv4"]
                    if "ipv4_addesses" in sub:
                        sub["ipv4_addesses"] += [ip]
                    else:
                        sub["ipv4_addesses"] = [ip]
                if is_ipv6_prefix(ip):
                    if "enabled_afi" in sub:
                        sub["enabled_afi"] += ["IPv6"]
                    else:
                        sub["enabled_afi"] = ["IPv6"]
                    if "ipv6_addesses" in sub:
                        sub["ipv6_addesses"] += [ip]
                    else:
                        sub["ipv6_addesses"] = [ip]
            match1 = self.rx_vlans.search(c)
            if match1:
                sub["tagged_vlans"] = self.expand_rangelist(match1.group("vlans"))
            match1 = self.rx_untagged.search(c)
            if match1:
                sub["untagged_vlan"] = int(match1.group("untagged"))
                if "tagged_vlans" in sub and sub["untagged_vlan"] in sub["tagged_vlans"]:
                    sub["tagged_vlans"].remove(sub["untagged_vlan"])
            if iftype in ["SubInt/L3", "Interface/L3"]:
                match1 = self.rx_vlan_id.search(c)
                if match1:
                    sub["vlan_ids"] = match1.group("vlan_id")
            if iftype == "Bridge/L2":
                for vrf in vrfs:
                    if vrf["forwarding_instance"] == match.group("vrf") and vrf["type"] in (
                        "VRF",
                        "table",
                    ):
                        vrf["interfaces"] += [iface]
                        bridge_name = iface["name"]
                        break
                continue
            if iftype == "SubInt/L3":
                for vrf in vrfs:
                    for i in vrf["interfaces"]:
                        if i["name"] == bridge_name:
                            i["subinterfaces"] += [sub]
                            break
                continue
            iface["subinterfaces"] += [sub]
            for vrf in vrfs:
                if vrf["forwarding_instance"] == match.group("vrf") and vrf["type"] in (
                    "VRF",
                    "table",
                ):
                    vrf["interfaces"] += [iface]
                    break

        return vrfs
