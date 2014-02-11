# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_interfaces
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
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaces, InterfaceTypeError
from noc.sa.profiles.Cisco.IOS import uBR


class Script(NOCScript):
    """
    Cisco.IOS.get_interfaces
    @todo: VRF support
    @todo: IPv6
    @todo: ISIS
    @todo: isis, bgp, rip
    @todo: subinterfaces
    @todo: Q-in-Q
    """
    name = "Cisco.IOS.get_interfaces"
    implements = [IGetInterfaces]

    TIMEOUT = 240

    rx_sh_int = re.compile(r"^(?P<interface>.+?)\s+is(?:\s+administratively)?\s+(?P<admin_status>up|down),\s+line\s+protocol\s+is\s+(?P<oper_status>up|down)\s(?:\((?:connected|notconnect|disabled|monitoring|err-disabled)\)\s*)?\n\s+Hardware is (?P<hardw>[^\n]+)\n(?:\s+Description:\s(?P<desc>[^\n]+)\n)?(?:\s+Internet address ((is\s(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}))|([^\d]+))\n)?[^\n]+\n[^\n]+\n\s+Encapsulation\s+(?P<encaps>[^\n]+)",
       re.MULTILINE | re.IGNORECASE)
    rx_sh_ip_int = re.compile(r"^(?P<interface>.+?)\s+is(?:\s+administratively)?\s+(?P<admin_status>up|down),\s+line\s+protocol\s+is\s+",
           re.IGNORECASE)
    rx_mac = re.compile(r"address\sis\s(?P<mac>\w{4}\.\w{4}\.\w{4})",
        re.MULTILINE | re.IGNORECASE)
    rx_ip = re.compile(r"Internet address is (?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})", re.MULTILINE | re.IGNORECASE)
    rx_sec_ip = re.compile(r"Secondary address (?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})", re.MULTILINE | re.IGNORECASE)
    rx_ipv6 = re.compile(
        r"(?P<address>\S+), subnet is (?P<net>\S+)/(?P<mask>\d+)",
        re.MULTILINE | re.IGNORECASE)
    rx_vlan_line = re.compile(r"^(?P<vlan_id>\d{1,4})\s+(?P<name>\S+)\s+(?P<status>active|suspend|act\/unsup)\s+(?P<ports>[\w\/\s\,\.]+)$", re.MULTILINE)
    rx_vlan_line_cont = re.compile(r"^\s{10,}(?P<ports>[\w\/\s\,\.]+)$",
        re.MULTILINE)
    rx_ospf = re.compile(r"^(?P<name>\S+)\s+\d", re.MULTILINE)
    rx_cisco_interface_name = re.compile(r"^(?P<type>[a-z]{2})[a-z\-]*\s*(?P<number>\d+(/\d+(/\d+)?)?([.:]\d+(\.\d+)?)?)$", re.IGNORECASE)

    types = {
           "As": "physical",    # Async
           "AT": "physical",    # ATM
           "At": "physical",    # ATM
           "Br": "physical",    # ISDN Basic Rate Interface
           "BD": "physical",    # Bridge Domain Interface
           "BV": "aggregated",  # BVI
           "Bu": "aggregated",  # Bundle
           "C": "physical",     # @todo: fix
           "Ca": "physical",    # Cable
           "CD": "physical",    # CDMA Ix
           "Ce": "physical",    # Cellular
           "Em": "physical",    # Embedded Service Engine
           "Et": "physical",    # Ethernet
           "Fa": "physical",    # FastEthernet
           "Fd": "physical",    # Fddi
           "Gi": "physical",    # GigabitEthernet
           "Gm": "physical",    # GMPLS
           "Gr": "physical",    # Group-Async
           "Lo": "loopback",    # Loopback
           "In": "physical",    # Integrated-service-engine
           "M": "management",   # @todo: fix
           "MF": "aggregated",  # Multilink Frame Relay
           "Mf": "aggregated",  # Multilink Frame Relay
           "Mu": "aggregated",  # Multilink-group interface
           "PO": "physical",    # Packet OC-3 Port Adapter
           "Po": "aggregated",  # Port-channel/Portgroup
           "R": "aggregated",   # @todo: fix
           "SR": "physical",    # Spatial Reuse Protocol
           "Sr": "physical",    # Spatial Reuse Protocol
           "Se": "physical",    # Serial
           "Te": "physical",    # TenGigabitEthernet
           "To": "physical",    # TokenRing
           "Tu": "tunnel",      # Tunnel
           "VL": "SVI",         # VLAN, found on C3500XL
           "Vl": "SVI",         # Vlan
           "Vo": "physical",    # Voice
           "XT": "SVI"          # Extended Tag ATM
           }

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

    rx_ifindex = re.compile(
        r"^(?P<interface>\S+): Ifindex = (?P<ifindex>\d+)")

    def get_ifindex(self):
        try:
            c = self.cli("show snmp mib ifmib ifindex")
        except self.CLISyntaxError:
            return {}
        r = {}
        for l in c.split("\n"):
            match = self.rx_ifindex.match(l.strip())
            if match:
                r[match.group("interface")] = int(match.group("ifindex"))
        return r

    ## Cisco uBR7100, uBR7200, uBR7200VXR, uBR10000 Series
    rx_vlan_ubr = re.compile(
        r"^\w{4}\.\w{4}\.\w{4}\s(?P<port>\S+)\s+(?P<vlan_id>\d{1,4})")

    def get_ubr_pvm(self):
        vlans = self.cli("show cable l2-vpn dot1q-vc-map")
        pvm = {}
        for l in vlans.split("\n"):
            match = self.rx_vlan_ubr.search(l)
            if match:
                port = match.group("port")
                vlan_id = int(match.group("vlan_id"))
                if port not in pvm:
                    pvm[port] = ["%s" % vlan_id]
                else:
                    pvm[port] += ["%s" % vlan_id]
        return pvm

    def execute(self):
        # Get port-to-vlan mappings
        pvm = {}
        switchports = {}  # interface -> (untagged, tagged)
        if self.match_version(uBR):
            # uBR series
            pvm = self.get_ubr_pvm()
        else:
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
        # Get LLDP interfaces
        lldp = self.get_lldp_interfaces()
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
            ip = match.group("ip")
            ipv4_interfaces[c_iface] += [ip]
        # Get IPv6 interfaces
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
        #
        interfaces = []
        # Get OSPF interfaces
        ospfs = self.get_ospfint()
        # Get interfaces SNMP ifIndex
        ifindex = self.get_ifindex()

        v = self.cli("show interface")
        for match in self.rx_sh_int.finditer(v):
            full_ifname = match.group("interface")
            ifname = self.profile.convert_interface_name(full_ifname)
            if ifname[:2] in ["Vi", "Di", "GM", "CP", "Nv", "Do", "Nu"]:
                continue
            # NOC-378 - Dirty hack for interface like ATM0/IMA0
            if "/ima" in full_ifname.lower():
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
                    if inm in lldp:
                        iface["enabled_protocols"] += ["LLDP"]
                    interfaces += [iface]
            a_stat = match.group("admin_status").lower() == "up"
            o_stat = match.group("oper_status").lower() == "up"
            hw = match.group("hardw")
            sub = {
                "name": ifname,
                "admin_status": a_stat,
                "oper_status": o_stat,
                "enabled_afi": [],
                "enabled_protocols": []
            }
            if "alias" in match.groups():
                sub["description"] = match.group("alias")
            if match.group("desc"):
                sub["description"] = match.group("desc")
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
            if match.group("encaps"):
                encaps = match.group("encaps")
                if encaps[:6] == "802.1Q":
                    sub["vlan_ids"] = [encaps.split(",")[1].split()[2][:-1]]
            # vtp
            # uBR ?
            if ifname in pvm:
                sub["vlan_ids"] = pvm[ifname]
            # IPv4/Ipv6
            if match.group("ip"):
                if ifname in ipv4_interfaces:
                    sub["enabled_afi"] += ["IPv4"]
                    sub["ipv4_addresses"] = ipv4_interfaces[ifname]
                if ifname in ipv6_interfaces:
                    sub["enabled_afi"] += ["IPv6"]
                    sub["ipv6_addresses"] = ipv6_interfaces[ifname]
            matchifn = self.rx_cisco_interface_name.match(ifname)
            shotn = (matchifn.group("type").capitalize() +
                     matchifn.group("number"))
            if shotn in ospfs:
                sub["enabled_protocols"] += ["OSPF"]

            if full_ifname in ifindex:
                sub["ifindex"] = ifindex[full_ifname]

            if "." not in ifname and ":" not in ifname:
                iface = {
                    "name": ifname,
                    "admin_status": a_stat,
                    "oper_status": o_stat,
                    "type": self.types[ifname[:2]],
                    "enabled_protocols": [],
                    "subinterfaces": [sub]
                }
                if ifname in lldp:
                    iface["enabled_protocols"] += ["LLDP"]
                if match.group("desc"):
                    iface["description"] = match.group("desc")
                if "mac" in sub:
                    iface["mac"] = sub["mac"]
                if "alias" in sub:
                    iface["alias"] = sub["alias"]
                # Set VLAN IDs for SVI
                if iface["type"] == "SVI":
                    sub["vlan_ids"] = [int(shotn[2:].strip())]
                # Portchannel member
                if ifname in portchannel_members:
                    ai, is_lacp = portchannel_members[ifname]
                    iface["aggregated_interface"] = ai
                    iface["enabled_protocols"] += ["LACP"]
                # Ifindex
                if full_ifname in ifindex:
                    iface["ifindex"] = ifindex[full_ifname]
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
