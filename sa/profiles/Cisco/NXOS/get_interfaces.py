# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.NXOS.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
from collections import defaultdict
from StringIO import StringIO
import xml.etree.ElementTree as ElementTree
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.base import InterfaceTypeError
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.lib.validators import is_int


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

    rx_int_split = re.compile(r"^\S", re.MULTILINE)
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
        r"\s+IPv6 address:\s+(?P<address>\S+)"
        r"\s+IPv6 subnet:\s+(?P<net>\S+)/(?P<mask>\d+)",
        re.MULTILINE | re.IGNORECASE)

    rx_ospf = re.compile(r"^(?P<name>\S+)\s+\d", re.MULTILINE)
    rx_cisco_interface_name = re.compile(
        r"^(?P<type>[a-z]{2})[a-z\-]*\s*(?P<number>\d+(/\d+(/\d+)?)?([.:]\d+(\.\d+)?)?(A|B)?)$",
        re.IGNORECASE)

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
            c = self.cli("show interface snmp-ifindex | xml | no-more")
            nsmap = {}
            r = {}
            for event, elem in ElementTree.iterparse(StringIO(c), events=("end", 'start-ns')):
                if event == 'start-ns':
                    ns, url = elem
                    nsmap[ns] = url
                if event == 'end':
                    if elem.tag == self.fixtag('', 'interface', nsmap):
                        full_ifname = elem.text.strip()
                    elif elem.tag == self.fixtag('', 'ifindex-dec', nsmap):
                        r[full_ifname] = int(elem.text.strip())
        except self.CLISyntaxError:
            try:
                c = self.cli("show interface snmp-ifindex")
                r = {}
                for ll in c.splitlines():
                    if ll == '' or '-' in ll or 'Port' in ll:
                        continue
                    match = ll.strip().split()
                    if match:
                        r[match[0]] = int(match[1])
            except self.CLISyntaxError:
                return {}
        return r

    def fixtag(self, ns, tag, nsmap):
        return '{' + nsmap[ns] + '}' + tag

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
        portchannel_dict = {}
        for pc in self.scripts.get_portchannel():
            i = pc["interface"]
            t = pc["type"] == "L"
            portchannel_dict = {i: []}
            for m in pc["members"]:
                portchannel_members[m] = (i, t)
                portchannel_dict[i] += [m]

        # Get IPv4 interfaces
        ipv4_interfaces = defaultdict(list)  # interface -> [ipv4 addresses]
        c_iface = None
        for ll in self.cli("show ip interface vrf all").splitlines():
            match = self.rx_sh_ip_int.search(ll)
            if match:
                c_iface = self.profile.convert_interface_name(
                    match.group("interface"))
                continue
            # Primary ip
            match = self.rx_ip.search(ll)
            if not match:
                # Secondary ip
                match = self.rx_sec_ip.search(ll)
                if not match:
                    continue
            ip = match.group("ip") + "/" + match.group("ipsubnet").split("/")[1]
            ipv4_interfaces[c_iface] += [ip]

        # Get IPv6 interfaces (may be might not work)
        ipv6_interfaces = defaultdict(list)  # interface -> [ipv6 addresses]
        c_iface = None
        try:
            v = self.cli("show ipv6 interface vrf all")
        except self.CLISyntaxError:
            v = ""
        for ll in v.splitlines():
            match = self.rx_sh_ip_int.search(ll)
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
            match = self.rx_ipv6.search(ll)
            if not match:
                # Secondary ip?
                continue
            ip = "%s/%s" % (match.group("address"), match.group("mask"))
            ipv6_interfaces[c_iface] += [ip]

        interfaces = []

        # Get interfaces SNMP ifIndex
        ifindex = self.get_ifindex()

        try:
            v = self.cli("show interface | xml | no-more")
            nsmap = {}
            results = []
            row = []
            for event, elem in ElementTree.iterparse(StringIO(v), events=("end", 'start-ns')):
                if event == 'start-ns':
                    ns, url = elem
                    nsmap[ns] = url
                if event == 'end':
                    if elem.tag == self.fixtag('', 'interface', nsmap):
                        full_ifname = elem.text.strip()
                        if full_ifname[:2] in ["Vi", "Di", "GM", "CP", "Nv", "Do", "Nu", "fc"]:
                            continue
                        results += [row]
                        row = {
                            "name": full_ifname,
                            "enabled_afi": [],
                            "enabled_protocols": []
                        }
                    if full_ifname.startswith("Vlan"):
                        if elem.tag == self.fixtag('', 'svi_line_proto', nsmap):
                            row["oper_status"] = elem.text.strip()
                        elif elem.tag == self.fixtag('', 'svi_admin_state', nsmap):
                            row["admin_status"] = elem.text
                        elif elem.tag == self.fixtag('', 'svi_desc', nsmap):
                            row["description"] = elem.text
                        elif elem.tag == self.fixtag('', 'svi_mac', nsmap):
                            row["mac"] = elem.text.strip()
                        elif elem.tag == self.fixtag('', 'svi_ip_addr', nsmap):
                            row["ip_addr"] = elem.text
                        continue
                    if elem.tag == self.fixtag('', 'state', nsmap):
                        row["oper_status"] = elem.text.strip()
                    elif elem.tag == self.fixtag('', 'state_rsn_desc', nsmap):
                        row["reason"] = elem.text
                    elif elem.tag == self.fixtag('', 'desc', nsmap):
                        row["description"] = elem.text
                    elif elem.tag == self.fixtag('', 'eth_hw_addr', nsmap):
                        row["mac"] = elem.text.strip()
                    elif elem.tag == self.fixtag('', 'eth_encap_vlan', nsmap):
                        row["vlan_ids"] = elem.text
                    elif elem.tag == self.fixtag('', 'eth_ip_addr', nsmap):
                        row["ip_addr"] = elem.text

            for I in results:
                if len(I) == 0:
                    continue
                full_ifname = I["name"]
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
                o_stat = I["oper_status"].lower() == "up"
                a_stat = False
                if "reason" in I:
                    a_stat = I["reason"].lower() != "administratively down"
                sub = {
                    "name": ifname,
                    "admin_status": a_stat,
                    "oper_status": o_stat,
                    "enabled_afi": [],
                    "enabled_protocols": []
                }
                # Get description
                if "description" in I:
                    sub["description"] = I["description"]
                # Get MAC
                if "mac" in I:
                    sub["mac"] = I["mac"]

                if ifname in switchports and ifname not in portchannel_members:
                    sub["enabled_afi"] += ["BRIDGE"]
                    u, t = switchports[ifname]
                    if u:
                        sub["untagged_vlan"] = u
                    if t:
                        sub["tagged_vlans"] = t

                # Static vlans
                if "vlan_ids" in I:
                    sub["vlan_ids"] = I["vlan_ids"]
                elif ifname.startswith("Vl "):
                    vlan_id = ifname[3:]
                    if is_int(vlan_id) and int(vlan_id) < 4095:
                        sub["vlan_ids"] = vlan_id

                # IPv4/Ipv6
                if "ip_addr" in I:
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

                    if "description" in I:
                        iface["description"] = I["description"]
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

        except self.CLISyntaxError:
            v = self.cli("show interface")

            for I in self.rx_int_split.split(v):
                if len(I) == 0:
                    continue
                match = self.rx_int_name.search(I)
                if not match:
                    continue
                full_ifname = match.group("interface")
                if full_ifname.startswith("th"):
                    full_ifname = 'E' + full_ifname
                elif full_ifname.startswith("lan"):
                    full_ifname = 'V' + full_ifname
                elif full_ifname.startswith("gmt"):
                    full_ifname = 'm' + full_ifname
                elif full_ifname.startswith("ort"):
                    full_ifname = 'p' + full_ifname
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
        r = self.scripts.get_mpls_vpn()
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
                    if v["name"] == "default":
                        continue
                    if i in portchannel_dict:
                        for i2 in portchannel_dict[i]:
                            imap[i2] = v["name"]

        for i in interfaces:
            subs = i["subinterfaces"]
            for vrf in set(imap.get(si["name"], "default") for si in subs):
                c = i.copy()
                c["subinterfaces"] = [si for si in subs
                                      if imap.get(si["name"], "default") == vrf]
                vrfs[vrf]["interfaces"] += [c]

        return vrfs.values()
