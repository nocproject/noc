# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOSXR.get_interfaces
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
from noc.sa.interfaces.base import InterfaceTypeError
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "Cisco.IOSXR.get_interfaces"
    interface = IGetInterfaces

    types = {
        "packet over sonet/sdh": "physical",
        "gigabitethernet/ieee 802.3 interface(s)": "physical",
        "fortygige": "physical",
        "tengige": "physical",
        "gigabitethernet": "physical",
        "management ethernet": "management",
        "aggregated ethernet interface(s)": "aggregated",
        "loopback interface(s)": "loopback",
        "null interface": "null",
        "tunnel-te": "tunnel",
        "vlan sub-interface(s)": None,
        "bridge-group virtual interface": "SVI"
    }

    rx_iface = re.compile(r"^(?P<name>\S+)\s+is\s+(?P<status>up|(?:administratively )?down),\s+"
                          r"line protocol is (?:up|(?:administratively )?down)\s*$", re.MULTILINE)

    rx_ip = re.compile(r"^Internet address is (?P<ip>\S+)\s*$", re.MULTILINE)

    rx_hw = re.compile(r"^Hardware is (?P<hw>.+?)(?:, address is (?P<mac>\S+).*)?$")

    rx_vlan_id = re.compile(r"^Encapsulation 802.1Q Virtual LAN, VLAN Id (?P<vlan>\d+),.*$",
        re.IGNORECASE)

    rx_bundle_member = re.compile(r"^(?P<name>\S+)\s+(?:Full|Half)-duplex\s+.+$",
        re.IGNORECASE)

    rx_ifindex = re.compile(r"^ifName : (?P<name>\S+)\s+ifIndex : (?P<ifindex>\d+)")


    def execute(self):
        ifaces = {}
        ifindex = self.get_ifindex_map()
        current = None
        is_bundle = False
        ae_map = {}  # member -> bundle
        v = self.cli("show interfaces")
        for l in v.splitlines():
            match = self.rx_iface.match(l)
            if match:
                current = self.profile.convert_interface_name(match.group("name"))
                status = match.group("status") == "up"
                ifaces[current] = {
                    "name": current,
                    "status": status
                }
                is_bundle = current.startswith("Bundle-Ether")
                if is_bundle:
                    ifaces[current]["members"] = []
                continue
            elif not current:
                continue
            l = l.strip()
            # Process description
            if l.startswith("Description:"):
                ifaces[current]["description"] = l[13:].strip()
                continue
            # Process IP addresses
            match = self.rx_ip.match(l)
            if match:
                ip = match.group("ip")
                if ip.lower() != "unknown":
                    ifaces[current]["addresses"] = (
                        ifaces[current].get("addresses", []) +
                        [ip]
                    )
                continue
            # Process hardware type and MAC
            match = self.rx_hw.match(l)
            if match:
                hw = match.group("hw").lower()
                t = self.types.get(hw, "unknown")
                if t == "unknown":
                    self.logger.error("Unknown hardware type: %s" % hw)
                ifaces[current]["type"] = t
                mac = match.group("mac")
                if mac:
                    ifaces[current]["mac"] = mac
            # Process VLAN id
            match = self.rx_vlan_id.match(l)
            if match:
                ifaces[current]["vlan_ids"] = [int(match.group("vlan"))]
            # Process ethernet bundles
            if is_bundle:
                match = self.rx_bundle_member.match(l)
                if match:
                    m = match.group("name")
                    ifaces[current]["members"] += [m]
                    if "." in current:
                        ae_map[m] = current.split(".", 1)[0]
                    else:
                        ae_map[m] = current
        # Get VRFs and "default" VRF interfaces
        r = []
        seen = set()
        vpns = self.scripts.get_mpls_vpn()
        for v in vpns:
            seen.update(v["interfaces"])
        vpns = [{
            "name": "default",
            "type": "ip",
            "interfaces": set(ifaces) - seen
            }] + vpns
        # Bring result together
        for fi in vpns:
            # Forwarding instance
            rr = {
                "forwarding_instance": fi["name"],
                "type": fi["type"],
                "interfaces": []
            }
            rd = fi.get("rd")
            if rd:
                rr["rd"] = rd
            # Get interface -> subinterfaces mapping
            p_ifaces = dict((x, []) for x in
                            set(i.split(".", 1)[0]
                                for i in fi["interfaces"]))
            for i in fi["interfaces"]:
                p = i.split(".", 1)[0]
                p_ifaces[p] += [i]
            # Create interfaces
            for iface in p_ifaces:
                if iface not in ifaces:
                    continue
                i = ifaces[iface]
                p = {
                    "name": self.profile.convert_interface_name(iface),
                    "type": i["type"],
                    "admin_status": i["status"],
                    "oper_status": i["status"],
                    "subinterfaces": []
                }
                if i.get("mac"):
                    p["mac"] = i["mac"]
                if i.get("description"):
                    p["description"] = i["description"]
                if p["name"] in ifindex:
                    p["snmp_ifindex"] = ifindex[p["name"]]
                if iface in ae_map:
                    # Bundle member
                    p["aggregated_interface"] = ae_map[iface]
                else:
                    # Create subinterfaces
                    for siface in p_ifaces[iface]:
                        if siface not in ifaces:
                            continue
                        ii = ifaces[siface]
                        sp = {
                            "name": self.profile.convert_interface_name(siface),
                            "admin_status": ii["status"],
                            "oper_status": ii["status"],
                            "enabled_afi": [],
                            "enabled_protocols": []
                        }
                        if ii.get("mac"):
                            sp["mac"] = ii["mac"]
                        if ii.get("description"):
                            sp["description"] = ii["description"]
                        if sp["name"] in ifindex:
                            sp["snmp_ifindex"] = ifindex[sp["name"]]
                        if ii.get("vlan_ids"):
                            sp["vlan_ids"] = ii["vlan_ids"]
                        # Process addresses
                        if "addresses" in ii:
                            ipv4_addresses = [a for a in ii["addresses"] if ":" not in a]
                            ipv6_addresses = [a for a in ii["addresses"] if ":" in a]
                            if ipv4_addresses:
                                sp["enabled_afi"] += ["IPv4"]
                                sp["ipv4_addresses"] = ipv4_addresses
                            if ipv6_addresses:
                                sp["enabled_afi"] += ["IPv6"]
                                sp["ipv6_addresses"] = ipv6_addresses
                        p["subinterfaces"] += [sp]
                rr["interfaces"] += [p]
            r += [rr]
        # Return result
        return r

    def get_ifindex_map(self):
        """
        Retrieve name -> ifindex map
        """
        m = {}
        if self.has_snmp():
            try:
                # IF-MIB::ifDescr
                t = self.snmp.get_table("1.3.6.1.2.1.2.2.1.2")
                for i in t:
                    if t[i].startswith("ControlEthernet"):
                        continue
                    m[self.profile.convert_interface_name(t[i])] = i
            except self.snmp.TimeOutError:
                pass
        else:
            s = self.cli("show snmp interface")
            for l in s.splitlines():
                match = self.rx_ifindex.match(l)
                if match:
                    if match.group("name").startswith("ControlEthernet"):
                        continue
                    m[self.profile.convert_interface_name(match.group("name"))] = match.group("ifindex")
        return m
