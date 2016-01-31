# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.AOS.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces, InterfaceTypeError
from noc.lib.ip import IPv4, IPv6


def ranges_to_list_str(s):
    # Python modules:
    import re
    rx_range = re.compile(r"^(\d+)\s*-\s*(\d+)$")
    r = []
    for p in s.split(","):
        p = p.strip()
        try:
            int(p)
            r += [p]
            continue
        except:
            pass
        match = rx_range.match(p)
        if not match:
            raise SyntaxError
        f, t = [int(x) for x in match.groups()]
        if f >= t:
            raise SyntaxError
        for i in range(f, t + 1):
            r += [str(i)]
        #    return sorted(r)
    return (r)


class Script(BaseScript):
    name = "Alcatel.AOS.get_interfaces"
    interface = IGetInterfaces

    rx_line = re.compile(r"\w*Slot/Port", re.MULTILINE)
    rx_name = re.compile(r"\s+(?P<name>.\S+)\s+:", re.MULTILINE)
    rx_mac_local = re.compile(r"\s+MAC address\s+: (?P<mac>.+),",
                              re.MULTILINE | re.IGNORECASE)
    rx_oper_status = re.compile(r"\s+Operational Status\s+: (?P<status>.+),",
                                re.MULTILINE | re.IGNORECASE)
    rx_sh_svi = re.compile(
        r"(?P<name>\S+)\s+(?P<ip>\d+.\d+.\d+.\d+)\s+(?P<mask>\d+.\d+.\d+.\d+)"
        r"\s+UP\s+YES\s+vlan\s+(?P<vlan>\d+)", re.MULTILINE | re.IGNORECASE)
    rx_ifindex_line = re.compile(r"Local Slot \d+\/Port \d+ LLDP Info:",
                                 re.MULTILINE | re.IGNORECASE)
    rx_ifindex = re.compile(r"\s+Port ID\s+=\s+(?P<ifindex>\d+)\s+\(Locally assigned\),",
                            re.MULTILINE | re.IGNORECASE)

    rx_ospf_gs = re.compile(r"\nOSPF status\s+=\s+Loaded,")
    rx_rip_gs = re.compile(r"\nRIP\s+status\s+=\s+Loaded,")
    rx_bgp_gs = re.compile(r"\nBGP\s+status\s+=\s+Loaded,")
    rx_dvmrp_gs = re.compile(r"\nDVMRP\s+status\s+=\s+Loaded,")
    rx_pim_gs = re.compile(r"\nPIM\s+status\s+=\s+Loaded,")
    rx_ripng_gs = re.compile(r"\nRIPng\s+status\s+=\s+Loaded,")
    rx_ospf3_gs = re.compile(r"\nOSPF3\s+status\s+=\s+Loaded,")
    rx_isis_gs = re.compile(r"\nISIS\s+status\s+=\s+Loaded,")
    rx_udld_gs = re.compile(r"Global\s+UDLD\s+(S|s)tatus\s+:\s+(e|E)nabled,")
    rx_lldp_gs = re.compile(r"System Name\s+=(|\s+)Alcatel\d+,")

    rx_lldp = re.compile(r"\n\s+(?P<port>.\S+\d+)\s+(Tx|Rx|Rx\s+\+\s+Tx)\s+", re.IGNORECASE)
    rx_ospf = re.compile(r"\n(?P<ipif>\S+)\s+\d+\.\d+\.\d+\.\d+\s+\d+\.\d+\.\d+\.\d+\s+", re.IGNORECASE)
    rx_rip = re.compile(r"\n(?P<ipif>\S+)\s+\d+\.\d+\.\d+\.\d+\s+\d+\.\d+\.\d+\.\d+\s+", re.IGNORECASE)
    rx_dvmrp = re.compile(r"\n(?P<ipif>\S+)\s+\d+\.\d+\.\d+\.\d+\s+\d+\.\d+\.\d+\.\d+\s+", re.IGNORECASE)
    rx_pim = re.compile(r"\n(?P<ipif>\S+)\s+\d+\.\d+\.\d+\.\d+\s+\d+\.\d+\.\d+\.\d+\s+", re.IGNORECASE)
    rx_ripng = re.compile(r"\n(?P<ipif>\S+)\s+\d+\.\d+\.\d+\.\d+\s+\d+\.\d+\.\d+\.\d+\s+", re.IGNORECASE)
    rx_ospf3 = re.compile(r"\n(?P<ipif>\S+)\s+\d+\.\d+\.\d+\.\d+\s+\d+\.\d+\.\d+\.\d+\s+", re.IGNORECASE)
    rx_isis = re.compile(r"\n(?P<ipif>\S+)\s+\d+\.\d+\.\d+\.\d+\s+\d+\.\d+\.\d+\.\d+\s+", re.IGNORECASE)
    rx_udld = re.compile(r"\n\s+(?P<port>.\S+\d+)\s+enabled\s+\S+", re.IGNORECASE)

    def execute(self):
        try:
            c = self.cli("show ip protocols")
        except self.CLISyntaxError:
            c = ""

        bgp = []
        bgp_enable = self.rx_bgp_gs.search(c) is not None
        if bgp_enable:
            try:
                c_if = self.cli("show ip bgp interface")
            except self.CLISyntaxError:
                c_if = ""
            for match in self.rx_bgp.finditer(c_if):
                bgp += [match.group("ipif")]

        ospf = []
        ospf_enable = self.rx_ospf_gs.search(c) is not None
        if ospf_enable:
            try:
                c_if = self.cli("show ip ospf interface")
            except self.CLISyntaxError:
                c_if = ""
            for match in self.rx_ospf.finditer(c_if):
                ospf += [match.group("ipif")]

        ospf3 = []
        ospf3_enable = self.rx_ospf3_gs.search(c) is not None
        if ospf3_enable:
            try:
                c_if = self.cli("show ip ospf3 interface")
            except self.CLISyntaxError:
                c_if = ""
            for match in self.rx_ospf3.finditer(c_if):
                ospf3 += [match.group("ipif")]

        rip = []
        rip_enable = self.rx_rip_gs.search(c) is not None
        if rip_enable:
            try:
                c_if = self.cli("show ip rip interface")
            except self.CLISyntaxError:
                c_if = ""
            for match in self.rx_rip.finditer(c_if):
                rip += [match.group("ipif")]

        ripng = []
        ripng_enable = self.rx_ripng_gs.search(c) is not None
        if ripng_enable:
            try:
                c_if = self.cli("show ip ripng interface")
            except self.CLISyntaxError:
                c_if = ""
            for match in self.rx_ripng.finditer(c_if):
                ripng += [match.group("ipif")]

        dvmrp = []
        dvmrp_enable = self.rx_dvmrp_gs.search(c) is not None
        if dvmrp_enable:
            try:
                c_if = self.cli("show ip dvmrp interface")
            except self.CLISyntaxError:
                c_if = ""
            for match in self.rx_dvmrp.finditer(c_if):
                dvmrp += [match.group("ipif")]

        pim = []
        pim_enable = self.rx_pim_gs.search(c) is not None
        if pim_enable:
            try:
                c_if = self.cli("show ip pim interface")
            except self.CLISyntaxError:
                c_if = ""
            for match in self.rx_pim.finditer(c_if):
                pim += [match.group("ipif")]

        isis = []
        isis_enable = self.rx_isis_gs.search(c) is not None
        if isis_enable:
            try:
                c_if = self.cli("show ip isis interface")
            except self.CLISyntaxError:
                c_if = ""
            for match in self.rx_isis.finditer(c_if):
                isis += [match.group("ipif")]

        lldp = []
        try:
            c = self.cli("show lldp local-system")
        except self.CLISyntaxError:
            c = ""
        lldp_enable = self.rx_lldp_gs.search(c) is not None
        if lldp_enable:
            try:
                c = self.cli("show lldp config")
            except self.CLISyntaxError:
                c = ""
            for match in self.rx_lldp.finditer(c):
                lldp += [match.group("port")]

        udld = []
        try:
            c = self.cli("show udld configuration")
        except self.CLISyntaxError:
            c = ""
        udld_enable = self.rx_udld_gs.search(c) is not None
        if udld_enable:
            try:
                c = self.cli("show udld status port")
            except self.CLISyntaxError:
                c = ""
            for match in self.rx_udld.finditer(c):
                udld += [match.group("port")]

        r = []
        try:
            v = self.cli("show interfaces")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        i = {
            "forwarding_instance": "default",
            "interfaces": [],
            "type": "physical"
        }
        switchports = {}
        for swp in self.scripts.get_switchport():
            switchports[swp["interface"]] = (
            swp["untagged"] if "untagged" in swp else None,
            swp["tagged"]
            )

        portchannel_members = {}
        for pc in self.scripts.get_portchannel():
            i = pc["interface"]
            print i
            t = pc["type"] == "L"
            print t
            for m in pc["members"]:
                portchannel_members[m] = (i, t)
            n = {}
            iface = "Ag %s" % i
            n["name"] = iface
            n["admin_status"] = True
            n["oper_status"] = True
            n["description"] = ""
            n["subinterfaces"] = [{
                "name": iface,
                "admin_status": True,
                "oper_status": True,
                "enabled_afi": ["BRIDGE"],
                "description": "",
            }]
            if switchports[iface][1]:
                n["subinterfaces"][0]["tagged_vlans"] = switchports[iface][1]
            if switchports[iface][0]:
                n["subinterfaces"][0]["untagged_vlan"] = switchports[iface][0]
            n["type"] = "aggregated"
            r += [n]
        v = "\n" + v

        for s in self.rx_line.split(v)[1:]:
            n = {}
            enabled_protocols = []
            match = self.rx_name.search(s)
            if not match:
                continue
            n["name"] = match.group("name")
            iface = n["name"]
            data1 = self.cli(
                "show lldp %s local-port" % iface)
            for match1 in self.rx_ifindex.finditer(data1):
                ifindex = match1.group("ifindex")
            else:
                ifindex = None
            if iface not in portchannel_members:
                match = self.rx_mac_local.search(s)
                if not match:
                    continue
                n["mac"] = match.group("mac")
                match = self.rx_oper_status.search(s)
                if not match:
                    continue
                n["oper_status"] = match.group("status")
                status = match.group("status").lower() == "up"
                n["admin_status"] = match.group("status")
                n["subinterfaces"] = [{
                    "name": iface,
                    "admin_status": True,
                    "oper_status": True,
                    "enabled_afi": ["BRIDGE"],
                    "mac": n["mac"],
                    "snmp_ifindex": ifindex,
                    "description": ""
                }]
                if switchports[iface][1]:
                    n["subinterfaces"][0]["tagged_vlans"] = switchports[iface][1]
                if switchports[iface][0]:
                    n["subinterfaces"][0]["untagged_vlan"] = switchports[iface][0]
                if lldp_enable  and iface in lldp:
                    enabled_protocols += ["LLDP"]
                if udld_enable  and iface in udld:
                    enabled_protocols += ["UDLD"]
                n["enabled_protocols"] = enabled_protocols
                n["type"] = "physical"
                r += [n]
            if iface in portchannel_members:
                ai, is_lacp = portchannel_members[iface]
                ai = "Ag %s" % ai
                n["aggregated_interface"] = ai
                n["enabled_protocols"] = ["LACP"]
                match = self.rx_mac_local.search(s)
                if not match:
                    continue
                n["mac"] = match.group("mac")
                match = self.rx_oper_status.search(s)
                if not match:
                    continue
                n["oper_status"] = match.group("status")
                status = match.group("status").lower() == "up"
                n["admin_status"] = match.group("status")
                n["subinterfaces"] = [{
                    "name": iface,
                    "admin_status": True,
                    "oper_status": True,
                    "enabled_afi": ["BRIDGE"],
                    "mac": n["mac"],
                    "snmp_ifindex": ifindex,
                    "description": ""
                }]
                n["type"] = "physical"
                r += [n]
        ip_int = self.cli("show ip interface")
        for match in self.rx_sh_svi.finditer(ip_int):
            ifname = match.group("name")
            ip = match.group("ip")
            enabled_afi = []
            enabled_protocols = []
            if ":" in ip:
                ip_interfaces = "ipv6_addresses"
                enabled_afi += ["IPv6"]
                ip = IPv6(ip, netmask=match.group("mask")).prefix
                ip_list = [ip]
            else:
                ip_interfaces = "ipv4_addresses"
                enabled_afi += ["IPv4"]
                ip = IPv4(ip, netmask=match.group("mask")).prefix
                ip_list = [ip]
            vlan = match.group("vlan")
            a_stat = "UP"
            print ifname
            if ospf_enable and ifname in ospf:
                enabled_protocols += ["OSPF"]
            if ospf3_enable and ifname in ospf3:
                enabled_protocols += ["OSPF3"]
            if pim_enable and ifname in pim:
                enabled_protocols += ["PIM"]
            if ripng_enable and ifname in ripng:
                enabled_protocols += ["RIPng"]
            if dvmrp_enable and ifname in dvmrp:
                enabled_protocols += ["DVMRP"]
            if isis_enable and ifname in isis:
                enabled_protocols += ["ISIS"]
            if bgp_enable and ifname in bgp:
                enabled_protocols += ["BGP"]
            print ifname
            iface = {
                "name": ifname,
                "type": "SVI",
                "admin_status": True,
                "oper_status": True,
                "description": "",
                "subinterfaces": [{
                    "name": ifname,
                    "enabled_protocols": enabled_protocols,
                    "description": ifname,
                    "admin_status": True,
                    "oper_status": True,
                    "enabled_afi": enabled_afi,
                    ip_interfaces: ip_list,
                    "vlan_ids": ranges_to_list_str(vlan),
                }]
            }
            r += [iface]
        return [{"interfaces": r}]
