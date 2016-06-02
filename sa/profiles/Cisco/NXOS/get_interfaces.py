# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.NXOS.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
# Python modules
import re
from collections import defaultdict
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces, InterfaceTypeError
from noc.sa.profiles.Cisco.IOS import uBR


class Script(BaseScript):
    """
    Cisco.NXOS.get_interfaces
    @todo: VRF support
    @todo: IPv6
    @todo: ISIS
    @todo: isis, bgp, rip
    @todo: subinterfaces
    @todo: Q-in-Q
    """
    name = "Cisco.NXOS.get_interfaces"
    interface = IGetInterfaces

    rx_int_split = re.compile(r"\n\n", re.MULTILINE)
    rx_int_name = re.compile(r"^(?P<interface>.+?)\s+is\s+(?P<oper_status>up|down)(?:\s\((?P<reason>\S+?)\))?",
                             re.MULTILINE | re.IGNORECASE)
    rx_int_description = re.compile(r"\s+(?:\s+Description:\s(?P<desc>[^\n]+)\n)",
                                    re.MULTILINE | re.IGNORECASE)
    rx_int_mac = re.compile(r"\s+Hardware[\s:](?:is)?\s(.+)?,\s+address[:\s](?:is)?\s+(?P<hardw>[^\n]+)?",
                            re.MULTILINE | re.IGNORECASE)
    rx_int_vlan = re.compile(r"\s+Encapsulation\s(?P<encaps>\S+)\sVirtual LAN,\sVlan\sID\s(?P<vlanid>\d+)",
                             re.MULTILINE | re.IGNORECASE)
    rx_int_ip = re.compile(r"\s+Internet address ((is\s(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}))|([^\d]+))\n",
                           re.MULTILINE | re.IGNORECASE)
    rx_mac = re.compile(r"^(?P<mac>\w{4}\.\w{4}\.\w{4})",
                        re.MULTILINE | re.IGNORECASE)

    rx_sh_ip_int = re.compile(
        r"^(?P<interface>\S+?), Interface status: protocol-(?P<protocol_status>up|down)\/"
        r"link-(?P<link_status>up|down)\/"
        r"admin-(?P<admin_status>up|down), iod: (?P<iod>\d+),",
        re.IGNORECASE)
    rx_ip = re.compile(
        r"IP address: (?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}), "
        r"IP subnet: (?P<ipsubnet>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})",
        re.MULTILINE | re.IGNORECASE)
    rx_sec_ip = re.compile(r"\s+(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}), "
                           r"IP subnet: (?P<ipsubnet>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})\s+secondary",
                           re.MULTILINE | re.IGNORECASE)
    rx_ipv6 = re.compile(
        r"(?P<address>\S+), subnet is (?P<net>\S+)/(?P<mask>\d+)",
        re.MULTILINE | re.IGNORECASE)

    rx_ospf = re.compile(r"^(?P<name>\S+)\s+\d", re.MULTILINE)
    rx_cisco_interface_name = re.compile(
        r"^(?P<type>[a-z]{2})[a-z\-]*\s*(?P<number>\d+(/\d+(/\d+)?)?([.:]\d+(\.\d+)?)?(A|B)?)$",
        re.IGNORECASE)
    rx_ctp = re.compile(r"Keepalive set \(\d+ sec\)")
    rx_lldp = re.compile("^(?P<iface>(?:Fa|Gi|Te)[^:]+?):.+Rx: (?P<rx_state>\S+)",
        re.MULTILINE | re.DOTALL)

    def get_lldp_interfaces(self):
        """
        Returns a set of normalized LLDP interface names
        :return:
        """
        try:
            v = self.cli("show lldp interface")
        except self.CLISyntaxError:
            return set()
        ports = set()
        for s in v.strip().split("\n\n"):
            match = self.rx_lldp.search(s)
            if match:
                if match.group("rx_state").lower() == "enabled":
                    ports.add(self.profile.convert_interface_name(match.group("iface")))
        return ports

    def get_ospfint(self):
        try:
            v = self.cli("show ip ospf interface brief")
        except self.CLISyntaxError:
            return []
        ospfs = []
        for s in v.split("\n"):
            match = self.rx_ospf.search(s)
            if match:
                ospfs += [match.group("name")]
        return ospfs

    def get_ifindex(self):
        try:
            c = self.cli("show interface snmp-ifindex")
        except self.CLISyntaxError:
            return {}
        r = {}
        for l in c.splitlines():
            if l == '' or '-' in l or 'Port' in l:
                continue
            match = l.strip().split()
            if match:
                r[match[0]] = int(match[1])
        return r

    def execute(self):
        # Get port-to-vlan mappings
        switchports = {}  # interface -> (untagged, tagged)
        vlans = None
        for cmd in ("show vlan brief", "show vlan-switch brief"):
            try:
                vlans = self.cli(cmd)
            except self.CLISyntaxError:
                continue
        if vlans:
            for sp in self.scripts.get_switchport():
                switchports[sp["interface"]] = (
                    sp["untagged"] if "untagged" in sp else None,
                    sp["tagged"]
                )

        # Get portchannels
        portchannel_members = {}
        for pc in self.scripts.get_portchannel():
            i = pc["interface"]
            t = pc["type"] == "L"
            for m in pc["members"]:
                portchannel_members[m] = (i, t)

        # Get IPv4 interfaces
        ipv4_interfaces = defaultdict(list)  # interface -> [ipv4 addresses]
        c_iface = None
        for l in self.cli("show ip interface").splitlines():
            match = self.rx_sh_ip_int.search(l)
            if match:
                c_iface = self.profile.convert_interface_name(
                    match.group("interface"))
                continue
            # Primary ip
            match = self.rx_ip.search(l)
            if not match:
                # Secondary ip
                match = self.rx_sec_ip.search(l)
                if not match:
                    continue
            ip = match.group("ip") + "/" + match.group("ipsubnet").split("/")[1]
            ipv4_interfaces[c_iface] += [ip]
        # Get IPv6 interfaces (may be might not work
        ipv6_interfaces = defaultdict(list)  # interface -> [ipv6 addresses]
        c_iface = None
        try:
            v = self.cli("show ipv6 interface")
        except self.CLISyntaxError:
            v = ""
        for l in v.splitlines():
            match = self.rx_sh_ip_int.search(l)
            if match:
                iface = match.group("interface")
                try:
                    c_iface = self.profile.convert_interface_name(iface)
                except InterfaceTypeError:
                    c_iface = None
                continue
            if not c_iface:
                continue  # Skip wierd interfaces
            # Primary ip
            match = self.rx_ipv6.search(l)
            if not match:
                # Secondary ip?
                continue
            ip = "%s/%s" % (match.group("address"), match.group("mask"))
            ipv6_interfaces[c_iface] += [ip]

        interfaces = []

        # Get interfaces SNMP ifIndex
        ifindex = self.get_ifindex()

        v = self.cli("show interface")
        for I in self.rx_int_split.split(v):
            if len(I) == 0:
                continue
            match = self.re_search(self.rx_int_name, I)
            full_ifname = match.group("interface")
            ifname = self.profile.convert_interface_name(full_ifname)
            if ifname[:2] in ["Vi", "Di", "GM", "CP", "Nv", "Do", "Nu", "fc"]:
                continue
            if ":" in ifname:
                inm = ifname.split(":")[0]
                # Create root interface if not exists yet
                if inm != interfaces[-1]["name"]:
                    iface = {
                        "name": inm,
                        "admin_status": True,
                        "oper_status": True,
                        "type": "physical",
                        "enabled_protocols": []
                    }
            o_stat = match.group("oper_status").lower() == "up"
            a_stat = False
            if match.group("reason"):
                a_stat = match.group("reason").lower() != "Administratively down"
            match = self.rx_int_mac.search(I)
            hw = match.group("hardw")
            sub = {
                "name": ifname,
                "admin_status": a_stat,
                "oper_status": o_stat,
                "enabled_afi": [],
                "enabled_protocols": []
            }
            # Get description
            match = self.rx_int_description.search(I)
            if match:
                sub["description"] = match.group("desc")
            # Get MAC
            matchmac = self.rx_mac.search(hw)
            if matchmac:
                sub["mac"] = matchmac.group("mac")
            if ifname in switchports and ifname not in portchannel_members:
                sub["enabled_afi"] += ["BRIDGE"]
                u, t = switchports[ifname]
                if u:
                    sub["untagged_vlan"] = u
                if t:
                    sub["tagged_vlans"] = t

            # Static vlans
            matchvlan = self.rx_int_vlan.search(I)
            if matchvlan:
                encaps = matchvlan.group("encaps")
                if encaps == "802.1Q":
                    sub["vlan_ids"] = matchvlan.group("vlanid")

            # IPv4/Ipv6
            matchip = self.rx_int_ip.search(I)
            if matchip:
                if ifname in ipv4_interfaces:
                    sub["enabled_afi"] += ["IPv4"]
                    sub["ipv4_addresses"] = ipv4_interfaces[ifname]
                if ifname in ipv6_interfaces:
                    sub["enabled_afi"] += ["IPv6"]
                    sub["ipv6_addresses"] = ipv6_interfaces[ifname]
            # Ifindex
            if full_ifname in ifindex:
                sub["snmp_ifindex"] = ifindex[full_ifname]

            if "." not in ifname and ":" not in ifname:
                iftype = self.profile.get_interface_type(ifname)
                if not iftype:
                    self.logger.info(
                        "Ignoring unknown interface type: '%s", iftype
                    )
                    continue
                iface = {
                    "name": ifname,
                    "admin_status": a_stat,
                    "oper_status": o_stat,
                    "type": iftype,
                    "enabled_protocols": [],
                    "subinterfaces": [sub]
                }
                match = self.rx_int_description.search(I)
                if match:
                    iface["description"] = match.group("desc")
                if "mac" in sub:
                    iface["mac"] = sub["mac"]
                # Portchannel member
                if ifname in portchannel_members:
                    ai, is_lacp = portchannel_members[ifname]
                    iface["aggregated_interface"] = ai
                    iface["enabled_protocols"] += ["LACP"]
                # Ifindex
                if full_ifname in ifindex:
                    iface["snmp_ifindex"] = ifindex[full_ifname]
                interfaces += [iface]
            else:
                # Append additional subinterface
                try:
                    interfaces[-1]["subinterfaces"] += [sub]
                except KeyError:
                    interfaces[-1]["subinterfaces"] = [sub]
        # Process VRFs
        vrfs = {
            "default": {
                "forwarding_instance": "default",
                "type": "ip",
                "interfaces": []
            }
        }
        imap = {}  # interface -> VRF
        try:
            r = self.scripts.get_mpls_vpn()
        except self.CLISyntaxError:
            r = []
        for v in r:
            if v["type"] == "VRF":
                vrfs[v["name"]] = {
                    "forwarding_instance": v["name"],
                    "type": "VRF",
                    "interfaces": []
                }
                rd = v.get("rd")
                if rd:
                    vrfs[v["name"]]["rd"] = rd
                for i in v["interfaces"]:
                    imap[i] = v["name"]
        for i in interfaces:
            subs = i["subinterfaces"]
            for vrf in set(imap.get(si["name"], "default") for si in subs):
                c = i.copy()
                c["subinterfaces"] = [si for si in subs
                                      if imap.get(si["name"], "default") == vrf]
                vrfs[vrf]["interfaces"] += [c]

        return vrfs.values()
