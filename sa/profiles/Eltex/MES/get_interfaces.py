# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.MES.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
from collections import defaultdict
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.lib.text import parse_table


class Script(BaseScript):
    """
    Eltex.MES.get_interfaces
    @todo: VRF support
    @todo: IPv6
    @todo: ISIS
    @todo: isis, bgp, rip
    @todo: subinterfaces
    @todo: Q-in-Q
    """

    name = "Eltex.MES.get_interfaces"
    cache = True
    interface = IGetInterfaces

    TIMEOUT = 300

    rx_sh_ip_int = re.compile(
        r"^(?P<ip>\d+\S+)/(?P<mask>\d+)\s+(?P<interface>.+?)\s+"
        r"((?P<admin_status>UP|DOWN)/(?P<oper_status>UP|DOWN)\s+)?"
        r"(?:Static|Dinamic|DHCP)\s", re.MULTILINE)
    rx_ifname = re.compile(
        r"^(?P<ifname>\S+)\s+\S+\s+(?:Enabled|Disabled).+$", re.MULTILINE)
    rx_sh_int = re.compile(
        r"^(?P<interface>.+?)\sis\s(?P<oper_status>up|down)\s+\((?P<admin_status>connected|not connected|admin.shutdown)\)\s*\n"
        r"^\s+Interface index is (?P<ifindex>\d+)\s*\n"
        r"^\s+Hardware is\s+.+?, MAC address is (?P<mac>\S+)\s*\n"
        r"(^\s+Description:(?P<descr>.*?)\n)?"
        r"^\s+Interface MTU is (?P<mtu>\d+)\s*\n"
        r"(^\s+Link aggregation type is (?P<link_type>\S+)\s*\n)?"
        r"(^\s+No. of members in this port-channel: \d+ \(active \d+\)\s*\n)?"
        r"((?P<members>.+?))?(^\s+Active bandwith is \d+Mbps\s*\n)?",
        re.MULTILINE | re.DOTALL)
    rx_sh_int_des = re.compile(
        r"^(?P<ifname>\S+)\s+\S+\s+(?:General|Access|Trunk|Customer|Promiscuous|Host)\s+\S+\s+(?P<oper_status>Up|Down)\s+(?P<admin_status>Up|Down|Not Present)\s*\n(?:^\s+Description:(?P<descr>.*?)\n)?",
        re.MULTILINE)
    rx_lldp_en = re.compile(r"LLDP state: Enabled?")
    rx_lldp = re.compile(r"^(?P<ifname>\S+)\s+(?:Rx and Tx|Rx|Tx)\s+", re.MULTILINE)

    rx_gvrp_en = re.compile(r"GVRP Feature is currently Enabled on the device?")
    rx_gvrp = re.compile(r"^(?P<ifname>\S+)\s+(?:Enabled\s+)Normal\s+", re.MULTILINE)

    rx_stp_en = re.compile(r"Spanning tree enabled mode?")
    rx_stp = re.compile(r"(?P<ifname>\S+)\s+(?:enabled)\s+\S+\s+\d+\s+\S+\s+\S+\s+(?:Yes|No)", re.MULTILINE)

    rx_vlan = re.compile(r"(?P<vlan>\S+)\s+(?P<vdesc>\S+)\s+(?P<vtype>Tagged|Untagged)\s+", re.MULTILINE)

    def execute(self):

        # Get portchannels
        portchannel_members = {}
        for pc in self.scripts.get_portchannel():
            i = pc["interface"]
            t = pc["type"] == "L"
            for m in pc["members"]:
                portchannel_members[m] = (i, t)

        # Get LLDP interfaces
        lldp = []
        c = self.cli("show lldp configuration", ignore_errors=True)
        if self.rx_lldp_en.search(c):
            lldp = self.rx_lldp.findall(c)

        # Get GVRP interfaces
        gvrp = []
        c = self.cli("show gvrp configuration", ignore_errors=True)
        if self.rx_gvrp_en.search(c):
            gvrp = self.rx_gvrp.findall(c)

        # Get STP interfaces
        stp = []
        c = self.cli("show spanning-tree", ignore_errors=True)
        if self.rx_stp_en.search(c):
            stp = self.rx_stp.findall(c)

        i = []
        c = self.cli("show interfaces description detailed")
        i = self.rx_sh_int_des.findall(c)

        interfaces = []
        mac = []
        ifindex = []
        mtu = []
        for res in i:
            name = res[0].strip()
            if self.match_version(version__regex="[12]\.[15]\.4[4-9]") \
            or self.match_version(version__regex="4\.0\.[4-5]"):
                v = self.cli("show interface %s" % name)
                for match in self.rx_sh_int.finditer(v):
                    ifname = match.group("interface")
                    ifindex = match.group("ifindex")
                    mac = match.group("mac")
                    mtu = match.group("mtu")
                    description = match.group("descr")
                    if not description:
                        description = ''
                    a_stat = match.group("admin_status").lower() == "connected"
                    o_stat = match.group("oper_status").lower() == "up"

            else:
                o_stat = res[1].strip().lower() == "up"
                a_stat = res[2].strip().lower() == "up"
                description = res[3].strip()

            iface = {
                "type": self.profile.get_interface_type(name),
                "name": self.profile.convert_interface_name(name),
                "mac": mac,
                "admin_status": a_stat,
                "oper_status": o_stat,
                "description": description.strip(),
                "snmp_ifindex": ifindex,
                "enabled_protocols": [],
                "subinterfaces": [{
                    "name": self.profile.convert_interface_name(name),
                    "mac": mac,
                    "mtu": mtu,
                    "admin_status": a_stat,
                    "oper_status": o_stat,
                    "description": description.strip(),
                    "snmp_ifindex": ifindex,
                    "enabled_afi": []
                }]
            }

            # LLDP protocol
            if name in lldp:
                iface["enabled_protocols"] += ["LLDP"]
            # GVRP protocol
            if name in gvrp:
                iface["enabled_protocols"] += ["GVRP"]
            # STP protocol
            if name in stp:
                iface["enabled_protocols"] += ["STP"]
                # Portchannel member
            name = self.profile.convert_interface_name(name)
            if name in portchannel_members:
                ai, is_lacp = portchannel_members[name]
                iface["aggregated_interface"] = ai
                if is_lacp:
                    iface["enabled_protocols"] += ["LACP"]
            cmd = self.cli("show interfaces switchport %s" % name)
            iface["subinterfaces"][0]["enabled_afi"] += ["BRIDGE"]
            # Vlans
            tvlan = []
            utvlan = None
            for vlan in parse_table(cmd):
                vlan_id = vlan[0]
                rule = vlan[2]
                if rule == "Tagged":
                    tvlan.append(int(vlan_id))
                elif rule == "Untagged":
                    utvlan = vlan_id
            iface["subinterfaces"][0]["tagged_vlans"] = tvlan
            if utvlan:
                iface["subinterfaces"][0]["untagged_vlan"] = utvlan

            interfaces += [iface]

        ip_iface = self.cli("show ip interface")
        for match in self.rx_sh_ip_int.finditer(ip_iface):
            ifname = match.group("interface")
            typ = self.profile.get_interface_type(ifname)
            ip = match.group("ip")
            netmask = match.group("mask")
            ip = ip + '/' + netmask
            ip_list = [ip]
            enabled_afi = []
            if ":" in ip:
                ip_interfaces = "ipv6_addresses"
                enabled_afi += ["IPv6"]
            else:
                ip_interfaces = "ipv4_addresses"
                enabled_afi += ["IPv4"]
            vlan = ifname.split(' ')[1]
            ifname = ifname.strip(' ')
            if match.group("admin_status"):
                a_stat = match.group("admin_status").lower() == "up"
            else:
                a_stat = True
            if match.group("oper_status"):
                o_stat = match.group("oper_status").lower() == "up"
            else:
                o_stat = True
            rx_vlan_name = re.compile(
                r"^\s*" + vlan + "\s+(?P<name>.+?)\s+\S+\s+\S+\s+\S+\s*$",
                re.MULTILINE)

            iface = {
                "name": self.profile.convert_interface_name(ifname),
                "type": typ,
                "admin_status": a_stat,
                "oper_status": o_stat,
                "subinterfaces": [{
                    "name": ifname,
                    "admin_status": a_stat,
                    "oper_status": o_stat,
                    "enabled_afi": enabled_afi,
                    ip_interfaces: ip_list,
                    "vlan_ids": self.expand_rangelist(vlan),
                }]
            }
            interfaces += [iface]

        return [{"interfaces": interfaces}]