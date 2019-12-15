# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# HP.Comware.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "HP.Comware.get_interfaces"
    interface = IGetInterfaces

    rx_sh_int = re.compile(
        r"^\s*(?P<interface>\S+) current state\s*:\s*(?P<oper_status>UP|DOWN|DOWN \( Administratively \))\s*\n"
        r"(^\s*Line protocol current state\s*:\s*(?P<line_status>UP|UP \(spoofing\)|DOWN|DOWN \( Administratively \))\s*\n)?"
        r"(^\s*IP (?:Packet Frame Type:|Sending Frames\' Format is) PKTFMT_ETHNT_2, Hardware Address(?: is|:) (?P<mac>\S+)\s*\n)?"
        r"^\s*Description\s*:(?P<descr>[^\n]*)\n",
        re.MULTILINE | re.IGNORECASE | re.DOTALL,
    )
    rx_mtu = re.compile(r"The Maximum Frame Length is (?P<mtu>\d+)")
    rx_port_type = re.compile(r"Port link-type: (?P<port_type>hybrid|access|trunk)")
    rx_port_other = re.compile(
        r"^\s*Tagged   VLAN ID : (?P<tagged>[^\n]+)\n"
        r"^\s*Untagged VLAN ID : (?P<untagged>[^\n]+)\n",
        re.MULTILINE,
    )
    rx_port_trunk = re.compile(
        r"^\s*VLAN passing  : (?P<passing>[^\n]+)\n" r"^\s*VLAN permitted: (?P<permitted>[^\n]+)\n",
        re.MULTILINE,
    )
    rx_ip = re.compile(r"Internet Address is (?P<ip>\S+) Primary")
    rx_ips = re.compile(r"Internet Address is (?P<ip>\S+) Sub")
    rx_mac = re.compile(
        r"IP (?:Packet Frame Type:|Sending Frames' Format is) PKTFMT_ETHNT_2, Hardware Address(?: is|:) (?P<mac>\S+)"
    )
    rx_sh_vlan = re.compile(
        r"^(?P<interface>\S+) current state\s*:\s*(?P<oper_status>UP|DOWN|DOWN \( Administratively \))\s*\n"
        r"^Line protocol current state\s*:\s*(?P<line_status>UP|UP \(spoofing\)|DOWN|DOWN \( Administratively \))\s*\n"
        r"(^IP (?:Packet Frame Type:|Sending Frames\' Format is) PKTFMT_ETHNT_2, Hardware address(?: is|:) (?P<mac>\S+)\s*\n)?"
        r"(^Internet Address is (?P<ip>\S+) Primary\s*\n)?"
        r"(^Internet protocol processing\s*:\s*\S+\s*\n)?"
        r"^Description\s*:(?P<descr>.*?)\n"
        r"^The Maximum Transmit Unit is (?P<mtu>\d+)",
        re.MULTILINE,
    )
    rx_name = re.compile(r"^Vlan-interface(?P<vlan>\d+)?")
    rx_isis = re.compile(r"Interface:\s+(?P<iface>\S+)")

    def execute(self):
        isis = []
        try:
            v = self.cli("display isis interface")
            for match in self.rx_isis.finditer(v):
                isis += [match.group("iface")]
        except self.CLISyntaxError:
            pass
        portchannel_members = {}
        for pc in self.scripts.get_portchannel():
            i = pc["interface"]
            t = pc["type"] == "L"
            for m in pc["members"]:
                portchannel_members[m] = (i, t)
        interfaces = []
        v = self.cli("display interface").split("\n\n")
        for i in v:
            match = self.rx_sh_int.search(i)
            if not match:
                continue
            ifname = match.group("interface")
            if ifname.startswith("Bridge-Aggregation") or ifname.startswith("Route-Aggregation"):
                iftype = "aggregated"
            elif ifname.startswith("LoopBack"):
                iftype = "loopback"
            elif ifname.startswith("Vlan-interface"):
                continue
            elif ifname.startswith("NULL"):
                continue
            else:
                iftype = "physical"
            o_stat = match.group("oper_status").lower() == "up"
            if match.group("oper_status") == "DOWN ( Administratively\)":
                a_stat = False
            else:
                a_stat = True
            iface = {
                "name": ifname,
                "type": iftype,
                "admin_status": a_stat,
                "oper_status": o_stat,
                "enabled_protocols": [],
                "subinterfaces": [],
            }
            sub = {
                "name": ifname,
                "admin_status": a_stat,
                "oper_status": o_stat,
                "enabled_afi": ["BRIDGE"],
                "enabled_protocols": [],
            }
            if ifname in isis:
                sub["enabled_protocols"] += ["ISIS"]
            if match.group("mac"):
                iface["mac"] = match.group("mac")
                sub["mac"] = match.group("mac")
            if match.group("descr"):
                iface["description"] = match.group("descr").strip()
                sub["description"] = match.group("descr").strip()
            match1 = self.rx_mtu.search(i)
            if match1:
                sub["mtu"] = int(match1.group("mtu"))
            match1 = self.rx_ip.search(i)
            if match1:
                sub["enabled_afi"] += ["IPv4"]
                sub["ipv4_addresses"] = [match1.group("ip")]
            match1 = self.rx_port_type.search(i)
            if match1:
                port_type = match1.group("port_type")
                if port_type in ["access", "hybrid"]:
                    match2 = self.rx_port_other.search(i)
                    if match2.group("untagged") and match2.group("untagged") != "none":
                        sub["untagged_vlan"] = int(match2.group("untagged"))
                    if match2.group("tagged") and match2.group("tagged") != "none":
                        sub["tagged_vlan"] = self.expand_rangelist(match2.group("tagged"))
                if port_type == "trunk":
                    match2 = self.rx_port_trunk.search(i)
                    if match2.group("passing") and match2.group("passing") != "none":
                        passing = match2.group("passing").replace("1(default vlan),", "")
                        sub["tagged_vlan"] = self.expand_rangelist(passing)
            iface["subinterfaces"] += [sub]
            if ifname in portchannel_members:
                ai, is_lacp = portchannel_members[ifname]
                iface["aggregated_interface"] = ai
                iface["enabled_protocols"] += ["LACP"]
            interfaces += [iface]
        v = self.cli("display interface Vlan-interface").split("\n\n")
        for i in v:
            match = self.rx_sh_vlan.search(i)
            if not match:
                continue
            ifname = match.group("interface")
            o_stat = match.group("oper_status").lower() == "up"
            if match.group("oper_status") == "DOWN ( Administratively\)":
                a_stat = False
            else:
                a_stat = True
            iface = {
                "name": ifname,
                "type": "SVI",
                "admin_status": a_stat,
                "oper_status": o_stat,
                "enabled_protocols": [],
                "subinterfaces": [],
            }
            sub = {"name": ifname, "admin_status": a_stat, "oper_status": o_stat, "enabled_afi": []}
            if match.group("descr"):
                iface["description"] = match.group("descr").strip()
                sub["description"] = match.group("descr").strip()
            if match.group("mtu"):
                sub["mtu"] = int(match.group("mtu"))
            match1 = self.rx_mac.search(i)
            if match1:
                iface["mac"] = match1.group("mac")
                sub["mac"] = match1.group("mac")
            match1 = self.rx_ip.search(i)
            if match1:
                sub["enabled_afi"] += ["IPv4"]
                sub["ipv4_addresses"] = [match1.group("ip")]
            match1 = self.rx_ips.search(i)
            if match1:
                sub["ipv4_addresses"] += [match1.group("ip")]
            vlan = self.rx_name.search(ifname).group("vlan")
            sub["vlan_ids"] = [vlan]
            iface["subinterfaces"] += [sub]
            interfaces += [iface]
        v = self.cli("display interface NULL").split("\n\n")
        for i in v:
            match = self.rx_sh_vlan.search(i)
            if not match:
                continue
            ifname = match.group("interface")
            o_stat = match.group("oper_status").lower() == "up (spoofing)"
            if match.group("oper_status") == "DOWN ( Administratively\)":
                a_stat = False
            else:
                a_stat = True
            iface = {
                "name": ifname,
                "type": "null",
                "admin_status": a_stat,
                "oper_status": o_stat,
                "enabled_protocols": [],
                "subinterfaces": [],
            }
            sub = {"name": ifname, "admin_status": a_stat, "oper_status": o_stat, "enabled_afi": []}
            if match.group("descr"):
                iface["description"] = match.group("descr").strip()
                sub["description"] = match.group("descr").strip()
            if match.group("mtu"):
                sub["mtu"] = int(match.group("mtu"))
            match1 = self.rx_mac.search(i)
            if match1:
                iface["mac"] = match1.group("mac")
                sub["mac"] = match1.group("mac")
            match1 = self.rx_ip.search(i)
            if match1:
                sub["enabled_afi"] += ["IPv4"]
                sub["ipv4_addresses"] = [match1.group("ip")]
            match1 = self.rx_ips.search(i)
            if match1:
                sub["ipv4_addresses"] += [match1.group("ip")]
            iface["subinterfaces"] += [sub]
            interfaces += [iface]
        return [{"interfaces": interfaces}]
