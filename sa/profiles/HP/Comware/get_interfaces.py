# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.Comware.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
# Python modules
import re
from collections import defaultdict
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "HP.Comware.get_interfaces"
    interface = IGetInterfaces

    rx_sh_int = re.compile(
        r"^\s*(?P<interface>\S+) current state: (?P<oper_status>UP|DOWN|DOWN \( Administratively \))\n"
        r"(^\s*IP Packet Frame Type: PKTFMT_ETHNT_2, Hardware Address: (?P<mac>\S+)\n)?"
        r"^\s*Description: (?P<descr>.+?)\n"
        r".*?"
        r"(^\s*The Maximum Frame Length is (?P<mtu>\d+)\n)?"
        r".+?"
        r"(^\s*Port link-type: (?P<port_type>hybrid|access|trunk)\n)?"
        r"(^\s*Tagged   VLAN ID : (?P<tagged>[^\n])\n)?"
        r"(^\s*Untagged VLAN ID : (?P<untagged>[^\n])\n)?"
        r"(^\s*VLAN passing  : (?P<passing>[^\n])\n)?"
        r"(^\s*VLAN permitted: (?P<permitted>[^\n])\n)?",
        re.MULTILINE | re.IGNORECASE | re.DOTALL)
    rx_sh_vlan = re.compile(
        r"^(?P<interface>\S+) current state: (?P<oper_status>UP|DOWN|DOWN \( Administratively \))\n"
        r"^Line protocol current state: (?P<line_status>UP|UP \(spoofing\)|DOWN|DOWN \( Administratively \))\n"
        r"^Description: (?P<descr>.+?)\n"
        r"^The Maximum Transmit Unit is (?P<mtu>\d+)\n"
        r".+?"
        r"(^\s*Internet Address is (?P<ip>\S+) Primary\n)?"
        r"(^\s*IP Packet Frame Type: PKTFMT_ETHNT_2, Hardware Address: (?P<mac>\S+)\n)?",
        re.MULTILINE | re.IGNORECASE | re.DOTALL)
    rx_name = re.compile(r"^Vlan-interface(?P<vlan>\d+)?")

    def execute(self):
        interfaces = []
        v = self.cli("display interface")
        for match in self.rx_sh_int.finditer(v):
            ifname = match.group("interface")
            if ifname.startswith("Bridge-Aggregation") \
            or ifname.startswith("Route-Aggregation"):
                iftype = "aggregated"
            elif ifname.startswith("LoopBack"):
                iftype = "loopback"
            elif ifname.startswith("NULL"):
                iftype = "null"
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
                "subinterfaces": []
            }
            sub = {
                "name": ifname,
                "admin_status": a_stat,
                "oper_status": o_stat,
                "enabled_afi": ["BRIDGE"]
            }
            if match.group("mac"):
                iface["mac"] = match.group("mac")
                sub["mac"] = match.group("mac")
            if match.group("mtu"):
                sub["mtu"] = int(match.group("mtu"))
            port_type = match.group("port_type")
            if port_type in ["access", "hybrid"]:
                if match.group("untagged") and match.group("untagged") != "none":
                    sub["untagged_vlan"] = int(match.group("untagged"))
                tagged = match.group("tagged")
                if match.group("tagged") and match.group("tagged") != "none":
                    sub["tagged_vlan"] = \
                    self.expand_rangelist(match.group("tagged"))
            if port_type == "trunk":
                if match.group("passing") and match.group("passing") != "none":
                    sub["tagged_vlan"] = \
                    self.expand_rangelist(match.group("passing"))
            iface["subinterfaces"] += [sub]
            interfaces += [iface]
        v = self.cli("display interface Vlan-interface")
        for match in self.rx_sh_vlan.finditer(v):
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
                "subinterfaces": []
            }
            sub = {
                "name": ifname,
                "admin_status": a_stat,
                "oper_status": o_stat,
                "enabled_afi": []
            }
            if match.group("mac"):
                iface["mac"] = match.group("mac")
                sub["mac"] = match.group("mac")
            if match.group("mtu"):
                sub["mtu"] = int(match.group("mtu"))
            if match.group("ip"):
                sub["enabled_afi"] += ["IPv4"]
                sub["ipv4_addresses"] = [match.group("ip")]
            vlan = self.rx_name.search(ifname).group("vlan")
            sub["vlan_ids"] = [vlan]
            iface["subinterfaces"] += [sub]
            interfaces += [iface]
        v = self.cli("display interface NULL")
        for match in self.rx_sh_vlan.finditer(v):
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
                "subinterfaces": []
            }
            sub = {
                "name": ifname,
                "admin_status": a_stat,
                "oper_status": o_stat,
                "enabled_afi": []
            }
            if match.group("mac"):
                iface["mac"] = match.group("mac")
                sub["mac"] = match.group("mac")
            if match.group("mtu"):
                sub["mtu"] = int(match.group("mtu"))
            if match.group("ip"):
                sub["enabled_afi"] += ["IPv4"]
                sub["ipv4_addresses"] = [match.group("ip")]
            iface["subinterfaces"] += [sub]
            interfaces += [iface]
        return [{"interfaces": interfaces}]
