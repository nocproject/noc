# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Eltex.MES.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import time
# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.sa.interfaces.base import MACAddressParameter
from noc.lib.text import parse_table


class Script(BaseScript):
=======
##----------------------------------------------------------------------
## Eltex.MES.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
from collections import defaultdict
# NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaces


class Script(NOCScript):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    """
    Eltex.MES.get_interfaces
    @todo: VRF support
    @todo: IPv6
    @todo: ISIS
    @todo: isis, bgp, rip
    @todo: subinterfaces
    @todo: Q-in-Q
    """
<<<<<<< HEAD

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
        r"^(?P<interface>.+?)\sis\s(?P<oper_status>up|down)\s+"
        r"\((?P<admin_status>connected|not connected|admin.shutdown|error-disabled)\)\s*\n"
        r"^\s+Interface index is (?P<ifindex>\d+)\s*\n"
        r"^\s+Hardware is\s+.+?, MAC address is (?P<mac>\S+)\s*\n"
        r"(^\s+Description:(?P<descr>.*?)\n)?"
        r"^\s+Interface MTU is (?P<mtu>\d+)\s*\n"
        r"(^\s+Link aggregation type is (?P<link_type>\S+)\s*\n)?"
        r"(^\s+No. of members in this port-channel: \d+ \(active \d+\)\s*\n)?"
        r"((?P<members>.+?))?(^\s+Active bandwith is \d+Mbps\s*\n)?",
        re.MULTILINE | re.DOTALL)
    rx_sh_int_des = rx_in = re.compile(r"^(?P<ifname>\S+)\s+(?P<oper_status>Up|Down)\s+"
                                       r"(?P<admin_status>Up|Down|Not Present)\s(?:(?P<descr>.*?)\n)?", re.MULTILINE)
    rx_sh_int_des2 = re.compile(r"^(?P<ifname>\S+\d+)(?P<descr>.*?)\n", re.MULTILINE)
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

    def execute_cli(self):
        d = {}
        if self.has_snmp():
            try:
                for s in self.snmp.getnext("1.3.6.1.2.1.2.2.1.2", max_repetitions=10):
                    n = s[1]
                    sifindex = s[0][len("1.3.6.1.2.1.2.2.1.2") + 1:]
                    if int(sifindex) < 3000:
                        sm = str(self.snmp.get("1.3.6.1.2.1.2.2.1.6.%s" % sifindex))
                        smac = MACAddressParameter().clean(sm)
                        if n.startswith("oob"):
                            continue
                        sname = self.profile.convert_interface_name(n)
                    else:
                        continue
                    d[sname] = {
                        "sifindex": sifindex,
                        "smac": smac
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
        i = self.rx_sh_int_des.findall("".join(["%s\n\n%s" % (c[0], c[1])]))
        if not i:
            i = self.rx_sh_int_des2.findall("".join(["%s\n\n%s" % (c[0], c[1])]))

        interfaces = []
        mtu = []
        for res in i:
            mac = None
            ifindex = 0
            name = res[0].strip()
            if (
                    self.match_version(version__regex="[12]\.[15]\.4[4-9]") or
                    self.match_version(version__regex="4\.0\.[4-7]$")
            ):
                v = self.cli("show interface %s" % name)
                time.sleep(1)
                for match in self.rx_sh_int.finditer(v):
                    ifname = match.group("interface")
                    ifindex = match.group("ifindex")
                    mac = match.group("mac")
                    mtu = match.group("mtu")
                    if len(res) == 4:
                        a_stat = res[1].strip().lower() == "up"
                        o_stat = res[2].strip().lower() == "up"
                        description = res[3].strip()
                    else:
                        a_stat = True
                        o_stat = match.group("oper_status").lower() == "up"
                        description = match.group("descr")
                        if not description:
                            description = ''

            else:
                if self.profile.convert_interface_name(name) in d:
                    ifindex = d[self.profile.convert_interface_name(name)]["sifindex"]
                    mac = d[self.profile.convert_interface_name(name)]["smac"]
                if len(res) == 4:
                    a_stat = res[1].strip().lower() == "up"
                    o_stat = res[2].strip().lower() == "up"
                    description = res[3].strip()
                else:
                    o_stat = True
                    a_stat = True
                    description = res[1].strip()

            sub = {
                "name": self.profile.convert_interface_name(name),
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
                "name": self.profile.convert_interface_name(name),
                "admin_status": a_stat,
                "oper_status": o_stat,
                "description": description.strip(),
                "enabled_protocols": [],
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
            name = self.profile.convert_interface_name(name)
            if name in portchannel_members:
                ai, is_lacp = portchannel_members[name]
                iface["aggregated_interface"] = ai
                if is_lacp:
                    iface["enabled_protocols"] += ["LACP"]
            iface["subinterfaces"][0]["enabled_afi"] += ["BRIDGE"]
            # Vlans
            cmd = self.cli("show interfaces switchport %s" % name)
            time.sleep(1)
            rcmd = cmd.split("\n\n")
            tvlan = []
            utvlan = None
            for vlan in parse_table(rcmd[0]):
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
            time.sleep(1)
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
=======
    name = "Eltex.MES.get_interfaces"
    implements = [IGetInterfaces]

    TIMEOUT = 240

    rx_sh_ip_int = re.compile(
           r"^(?P<ip>\S+)/(?P<mask>\d+)\s+(?P<interface>.+)\s+(Static|Dinamic)\s+(Valid|Invalid)\s*$",
           re.MULTILINE)

    rx_status = re.compile(
           r"^(?P<interface>\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(?P<oper_status>Up|Down).+$",
           re.MULTILINE)

    types = {
           "As": "physical",    # Async
           "AT": "physical",    # ATM
           "At": "physical",    # ATM
           "BV": "aggregated",  # BVI
           "Bu": "aggregated",  # Bundle
           "C": "physical",     # @todo: fix
           "Ca": "physical",    # Cable
           "CD": "physical",    # CDMA Ix
           "Ce": "physical",    # Cellular
           "et": "physical",    # Ethernet
           "Fa": "physical",    # FastEthernet
           "Gi": "physical",    # GigabitEthernet
           "Gr": "physical",    # Group-Async
           "Lo": "loopback",    # Loopback
           "M": "management",   # @todo: fix
           "MF": "aggregated",  # Multilink Frame Relay
           "Mf": "aggregated",  # Multilink Frame Relay
           "Mu": "aggregated",  # Multilink-group interface
           "PO": "physical",    # Packet OC-3 Port Adapter
           "Po": "aggregated",  # Port-channel/Portgroup
           "po": "aggregated",  # Port-channel/Portgroup
           "R": "aggregated",   # @todo: fix
           "SR": "physical",    # Spatial Reuse Protocol
           "Se": "physical",    # Serial
           "Te": "physical",    # TenGigabitEthernet
           "Tu": "tunnel",      # Tunnel
           "VL": "SVI",         # VLAN, found on C3500XL
           "Vl": "SVI",         # Vlan
           "XT": "SVI"          # Extended Tag ATM
           }

    def get_ospfint(self):
        ospfs = []
        return ospfs

    def execute(self):
        # Get port-to-vlan mappings
        pvm = {}
        switchports = {}  # interface -> (untagged, tagged)
        vlans = None
        cmd = "show vlan"
        try:
            vlans = self.cli(cmd)
        except self.CLISyntaxError:
            pass
        if vlans:
            for sp in self.scripts.get_switchport():
                switchports[sp["interface"]] = (
                    sp["untagged"] if "untagged" in sp else None,
                    sp["tagged"]
                    )

        # Get OSPF interfaces
        ospfs = self.get_ospfint()

        # Get IP interfaces
        mac = self.scripts.get_chassis_id()[0]
        mac = mac['first_chassis_mac']
        interfaces = []
        ip_iface = self.cli("show ip interface")
        for match in self.rx_sh_ip_int.finditer(ip_iface):
            ifname = match.group("interface")
            ip = match.group("ip")
            netmask = match.group("mask")
            enabled_afi = []
            if ":" in ip:
                ip_interfaces = "ipv6_addresses"
                ip_ver = "is_ipv6"
                enabled_afi += ["IPv6"]
                ip = ip + '/' +  netmask
                ip_list = [ip]
            else:
                ip_interfaces = "ipv4_addresses"
                ip_ver = "is_ipv4"
                enabled_afi += ["IPv4"]
                ip = ip + '/' + netmask
                ip_list = [ip]
            vlan = ifname.split(' ')[1]
            ifname = ifname.strip(' ')
            a_stat = True  # match.group("admin_status").lower() == "up"
            o_stat = True  # match.group("oper_status").lower() == "up"
            rx_vlan_name = re.compile(
                r"^\s*" + vlan + "\s+(?P<name>.+?)\s+\S+\s+\S+\s+\S+\s*$",
                re.MULTILINE)
            name = rx_vlan_name.search(vlans)
            description = ifname + ' ' + name.group("name")
            iface = {
                "name": ifname,
                "type": "SVI",
                "admin_status": a_stat,
                "oper_status": o_stat,
                "mac": mac,
                "description": description,
                "subinterfaces": [{
                        "name": ifname,
                        "description": description,
                        "admin_status": a_stat,
                        "oper_status": o_stat,
                        ip_ver: True,
                        "enabled_afi": enabled_afi,
                        ip_interfaces: ip_list,
                        "mac": mac,
                        "vlan_ids": self.expand_rangelist(vlan),
                        #"snmp_ifindex": 
                    }]
                }
            interfaces += [iface]

        # Get portchannels
        portchannel_members = {}
        for pc in self.scripts.get_portchannel():
            i = pc["interface"]
            t = pc["type"] == "L"
            for m in pc["members"]:
                portchannel_members[m] = (i, t)

        status = self.cli("show interfaces status")
        config = self.cli("show interfaces configuration")
        descr = self.cli("show interfaces description")
        for match in self.rx_status.finditer(status):
            ifname = match.group("interface")
            o_stat = match.group("oper_status").lower() == "up"
            rx_config = re.compile(
                r"^" + ifname + "\s+\S+\s+(\S+\s+|)\d+\s+\S+\s+\S+\s+(?P<admin_status>(Up|Down))(\s+\S+\s+\S+|)",
                re.MULTILINE)
            match = rx_config.search(config)
            a_stat = match.group("admin_status").lower() == "up"
            rx_descr = re.compile(
                r"^" + ifname + "\s+(?P<desc>\S+)$", re.MULTILINE)
            match = rx_descr.search(descr)
            if match:
                description = match.group("desc")
            else:
                description = ''

            ifname = ifname.replace('fa', 'Fa ')
            ifname = ifname.replace('gi', 'Gi ')
            ifname = ifname.replace('te', 'Te ')
            ifname = ifname.replace('Po', 'Po ')
            iface = {
                    "name": ifname,
                    "type": self.types[ifname[:2]],
                    "admin_status": a_stat,
                    "oper_status": o_stat,
                    "mac": mac,
                    "description": description,
                    "subinterfaces": [{
                            "name": ifname,
                            "description": description,
                            "admin_status": a_stat,
                            "oper_status": o_stat,
                            "mac": mac,
#                            "snmp_ifindex": self.scripts.get_ifindex(interface=ifname)
                        }]
                    }

            # Portchannel member
            if ifname in portchannel_members:
                ai, is_lacp = portchannel_members[ifname]
                iface["aggregated_interface"] = ai
                if is_lacp:
                    iface["enabled_protocols"] = ["LACP"]
            else:
#                iface["subinterfaces"][0]["is_bridge"] = True
                iface["subinterfaces"][0]["enabled_afi"] = ["BRIDGE"]
                if switchports[ifname][1]:
                    iface["subinterfaces"][0]["tagged_vlans"] = switchports[ifname][1]
                if switchports[ifname][0]:
                    iface["subinterfaces"][0]["untagged_vlan"] = switchports[ifname][0]

>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            interfaces += [iface]

        return [{"interfaces": interfaces}]
