# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Planet.WGSD.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.lib.text import parse_table
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.sa.interfaces.base import MACAddressParameter


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

    name = "Planet.WGSD.get_interfaces"
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
        r"^(?P<interface>.+?)\sis\s(?P<oper_status>up|down)\s+"
        r"\((?P<admin_status>connected|not connected|admin.shutdown)\)\s*\n"
        r"^\s+Interface index is (?P<ifindex>\d+)\s*\n"
        r"^\s+Hardware is\s+.+?, MAC address is (?P<mac>\S+)\s*\n"
        r"(^\s+Description:(?P<descr>.*?)\n)?"
        r"^\s+Interface MTU is (?P<mtu>\d+)\s*\n"
        r"(^\s+Link aggregation type is (?P<link_type>\S+)\s*\n)?"
        r"(^\s+No. of members in this port-channel: \d+ \(active \d+\)\s*\n)?"
        r"((?P<members>.+?))?(^\s+Active bandwith is \d+Mbps\s*\n)?",
        re.MULTILINE | re.DOTALL)
    rx_sh_int_des = re.compile(
        r"^(?P<ifname>\S+)\s+(?P<oper_status>Up|Down)"
        r"\s+(?P<admin_status>Up|Down|Not Present)\s(?:(?P<descr>.*?)\n)?",
        re.MULTILINE)
    rx_sh_int_des2 = re.compile(
        r"^(?P<ifname>\S+\d+)(?P<descr>.*?)\n", re.MULTILINE)
    rx_lldp_en = re.compile(r"LLDP state: Enabled?")
    rx_lldp = re.compile(
        r"^(?P<ifname>\S+)\s+(?:Rx and Tx|Rx|Tx)\s+", re.MULTILINE)

    rx_gvrp_en = re.compile(
        r"GVRP Feature is currently Enabled on the device?")
    rx_gvrp = re.compile(
        r"^(?P<ifname>\S+)\s+(?:Enabled\s+)Normal\s+", re.MULTILINE)

    rx_stp_en = re.compile(r"Spanning tree enabled mode?")
    rx_stp = re.compile(
        r"(?P<ifname>\S+)\s+(?:enabled)\s+\S+\s+\d+\s+\S+\s+\S+\s+(?:Yes|No)",
        re.MULTILINE)

    rx_vlan = re.compile(
        r"(?P<vlan>\S+)\s+(?P<vdesc>\S+)\s+(?P<vtype>Tagged|Untagged)\s+",
        re.MULTILINE)

    def execute(self):
        d = {}

        if self.has_snmp():
            try:
                for s in self.snmp.getnext("1.3.6.1.2.1.31.1.1.1.1"):
                    n = s[1]
                    sifindex = s[0][len("1.3.6.1.2.1.31.1.1.1.1") + 1:]
                    if int(sifindex) < 1000:
                        sm = str(self.snmp.get("1.3.6.1.2.1.2.2.1.6.%s" % sifindex))
                        mtu = self.snmp.get("1.3.6.1.2.1.2.2.1.4.%s" % sifindex)
                        smac = MACAddressParameter().clean(sm)
                    else:
                        continue
                    d[n] = {
                        "sifindex": sifindex,
                        "smac": smac,
                        "mtu": mtu
                    }
            except self.snmp.TimeOutError:
                pass

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

        # Get ifname and description
        i = []
        c = self.cli("show interfaces description").split("\n\n")
        i = self.rx_sh_int_des.findall(c[0])
        if not i:
            i = self.rx_sh_int_des2.findall(c[0])

        interfaces = []
        for res in i:
            mac = None
            ifindex = 0
            name = res[0].strip()
            if name in d:
                ifindex = d[name]["sifindex"]
                mac = d[name]["smac"]
                mtu = d[name]["mtu"]
            if len(res) == 4:
                o_stat = res[1].strip().lower() == "up"
                a_stat = res[2].strip().lower() == "up"
                description = res[3].strip()
            else:
                o_stat = True
                a_stat = True
                description = res[1].strip()

            sub = {
                "name": name,
                "mtu": mtu,
                "admin_status": a_stat,
                "oper_status": o_stat,
                "description": description.strip(),
                "enabled_afi": []
            }
            if ifindex:
                sub["snmp_ifindex"] = ifindex
            if mac:
                sub["mac"] = mac
            iface = {
                "type": self.profile.get_interface_type(name),
                "name": name,
                "admin_status": a_stat,
                "oper_status": o_stat,
                "enabled_protocols": [],
                "description": description.strip(),
                "subinterfaces": [sub]
            }
            if ifindex:
                iface["snmp_ifindex"] = ifindex
            if mac:
                iface["mac"] = mac

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
            if name in portchannel_members:
                ai, is_lacp = portchannel_members[name]
                iface["aggregated_interface"] = ai
                if is_lacp:
                    iface["enabled_protocols"] += ["LACP"]
            iface["subinterfaces"][0]["enabled_afi"] += ["BRIDGE"]
            # Vlans
            cmd = self.cli("show interfaces switchport ethernet %s" % name)
            rcmd = cmd.split("\n\n")
            tvlan = []
            utvlan = None
            for vlan in parse_table(rcmd[1]):
                vlan_id = vlan[0]
                rule = vlan[2]
                if rule == "Tagged":
                    tvlan.append(int(vlan_id))
                elif rule == "Untagged":
                    utvlan = vlan_id
            iface["subinterfaces"][0]["tagged_vlans"] = tvlan
            if utvlan:
                iface["subinterfaces"][0]["untagged_vlan"] = utvlan
            cmd = self.cli("show ip interface %s" % name)
            for match in self.rx_sh_ip_int.finditer(cmd):
                if not match:
                    continue
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
                iface["subinterfaces"][0]["enabled_afi"] = enabled_afi
                iface["subinterfaces"][0][ip_interfaces] = ip_list

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
            if ifname.startswith("vlan"):
                vlan = ifname.split(' ')[1]
                ifname = ifname.strip()
            else:
                continue
            if match.group("admin_status"):
                a_stat = match.group("admin_status").lower() == "up"
            else:
                a_stat = True
            if match.group("oper_status"):
                o_stat = match.group("oper_status").lower() == "up"
            else:
                o_stat = True
            iface = {
                "name": ifname,
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
