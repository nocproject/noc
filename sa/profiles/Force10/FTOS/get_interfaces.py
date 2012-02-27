# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Force10.FTOS.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaces


class Script(NOCScript):
    """
    Force10.FTOS.get_interfaces

    @todo: VRF support
    @todo: IPv6
    @todo: ISIS
    @todo: secondary addresses
    @todo: isis, ospf, bgp, rip
    @todo: ip unnumbered
    @todo: subinterfaces
    @todo: Q-in-Q
    """
    name = "Force10.FTOS.get_interfaces"
    implements = [IGetInterfaces]

    types = {
        "gi": "physical",
        "te": "physical",
        "fa": "physical",
        "vl": "SVI",
        "po": "aggregated",
        "lo": "loopback",
        "ma": "management"
    }

    rx_sh_int = re.compile(
        r"^(?P<interface>.+?)\s+is\s+(?P<admin_status>up|down),\s+line\s+protocol\s+is\s+(?P<oper_status>up|down|not present)",
        re.MULTILINE | re.IGNORECASE)
    rx_int_alias = re.compile(
        r"^(Description|Vlan alias name is):\s*(?P<alias>.*?)$",
        re.MULTILINE | re.IGNORECASE)
    rx_int_mac = re.compile(r"Current\s+address\s+is\s+(?P<mac>\S+)",
                            re.MULTILINE | re.IGNORECASE)
    rx_int_ipv4 = re.compile(r"^Internet address is (?P<address>[0-9]\S+)",
                             re.MULTILINE | re.IGNORECASE)
    rx_int_ifindex = re.compile(r"^Interface index is (?P<ifindex>\d+)",
                                re.MULTILINE | re.IGNORECASE)

    def execute(self):
        # Get portchannes
        portchannel_members = {}  # member -> (portchannel, type)
        for pc in self.scripts.get_portchannel():
            i = pc["interface"]
            t = pc["type"] == "L"
            for m in pc["members"]:
                portchannel_members[m] = (i, t)
        # Get switchports
        switchports = {}  # interface -> (untagged, tagged)
        for sp in self.scripts.get_switchport():
            switchports[sp["interface"]] = (sp["untagged"] if "untagged" in sp
                                            else None, sp["tagged"])
        # Get interfaces
        interfaces = []
        v = self.cli("show interfaces")
        for s in v.split("\n\n"):
            s = s.strip()
            if not s:
                continue
            match = self.re_match(self.rx_sh_int, s)
            ifname = self.profile.convert_interface_name(
                match.group("interface"))
            try:
                ift = self.types[ifname.lower()[:2]]
            except KeyError:
                raise self.UnexpectedResultError(
                    "Cannot determine interface type for: '%s'" % ifname)
            admin_status = match.group("admin_status").lower() == "up"
            oper_status = match.group("oper_status").lower() in ("up",
                                                                 "not present")
            iface = {
                "name": ifname,
                "admin_status": admin_status,
                "oper_status": oper_status,
                "type": ift,
                }
            # Get description
            description = None
            match = self.rx_int_alias.search(s)
            if match:
                description = match.group("alias")
                iface["description"] = description
            # Get MAC
            match = self.rx_int_mac.search(s)
            if match:
                iface["mac"] = match.group("mac")
            # Process portchannel members
            if ifname in portchannel_members:
                iface["aggregated_interface"] = portchannel_members[ifname][0]
                iface["is_lacp"] = portchannel_members[ifname][1]
            # Process subinterfaces
            subinterfaces = []
            if "aggregated_interface" not in iface:
                sub = {
                    "name": ifname,
                    "admin_status": admin_status,
                    "oper_status": oper_status,
                    }
                # IPv4 addresses
                match = self.rx_int_ipv4.search(s)
                if match:
                    sub["is_ipv4"] = True
                    sub["ipv4_addresses"] = [match.group("address")]
                # ifIndex
                match = self.rx_int_ifindex.search(s)
                if match:
                    sub["snmp_ifindex"] = match.group("ifindex")
                # Set VLAN IDs for SVI
                if ift == "SVI":
                    sub["vlan_ids"] = [int(ifname[3:].strip())]
                # Set switchports
                if ifname in switchports:
                    sub["is_bridge"] = True
                    u, t = switchports[ifname]
                    if u:
                        sub["untagged_vlan"] = u
                    if t:
                        sub["tagged_vlans"] = t
                if (sub.get("is_ipv4") or sub.get("is_ipv6") or
                    sub.get("is_iso") or sub.get("is_mpls") or
                    sub.get("is_bridge")):
                    subinterfaces += [sub]
            # Append to interfaces
            iface["subinterfaces"] = subinterfaces
            if subinterfaces or "aggregated_interface" in iface:
                interfaces += [iface]
        # Get interfaces
        return [{"interfaces": interfaces}]
