# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.MES.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
from collections import defaultdict
# NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaces


class Script(NOCScript):
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
    implements = [IGetInterfaces]

    TIMEOUT = 300

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
        for sp in self.scripts.get_switchport():
            switchports[sp["interface"]] = (
                sp["untagged"] if "untagged" in sp else None,
                sp["tagged"]
                )

        vlans = None
        cmd = "show vlan"
        try:
            vlans = self.cli(cmd)
        except self.CLISyntaxError:
            pass

        # Get OSPF interfaces
        ospfs = self.get_ospfint()

        # Get IP interfaces
        mac = self.scripts.get_chassis_id()
        mac = mac[0]['first_chassis_mac']
        interfaces = []
        ip_iface = self.cli("show ip interface")
        for match in self.rx_sh_ip_int.finditer(ip_iface):
            ifname = match.group("interface")
            typ = self.types[ifname[:2]]
            ip = match.group("ip")
            netmask = match.group("mask")
            ip = ip + '/' +  netmask
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
            a_stat = True  # match.group("admin_status").lower() == "up"
            o_stat = True  # match.group("oper_status").lower() == "up"
            rx_vlan_name = re.compile(
                r"^\s*" + vlan + "\s+(?P<name>.+?)\s+\S+\s+\S+\s+\S+\s*$",
                re.MULTILINE)
            name = rx_vlan_name.search(vlans)
            description = ifname + ' ' + name.group("name")

            iface = {
                "name": ifname,
                "type": typ,
                "admin_status": a_stat,
                "oper_status": o_stat,
                "mac": mac,
                "description": description,
                "subinterfaces": [{
                        "name": ifname,
                        "description": description,
                        "admin_status": a_stat,
                        "oper_status": o_stat,
                        "enabled_afi": enabled_afi,
                        ip_interfaces: ip_list,
                        "mac": mac,
                        "vlan_ids": self.expand_rangelist(vlan),
                        #"snmp_ifindex": 
                    }]
                }
            interfaces += [iface]

        status = self.cli("show interfaces status")
        config = self.cli("show interfaces configuration")
        descr = self.cli("show interfaces description")
        gvrp = self.cli("show gvrp configuration")
        lldp = self.cli("show lldp configuration")
        stp = self.cli("show spanning-tree")

        # Get portchannels
        portchannel_members = {}
        for pc in self.scripts.get_portchannel():
            i = pc["interface"]
            t = pc["type"] == "L"
            for m in pc["members"]:
                portchannel_members[m] = (i, t)

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
                    "enabled_protocols": [],
#                    "snmp_ifindex": self.scripts.get_ifindex(interface=ifname)
                    "subinterfaces": [{
                        "name": ifname,
                        "description": description,
                        "admin_status": a_stat,
                        "oper_status": o_stat,
                        "mac": mac,
                        "enabled_afi": [],
#                        "snmp_ifindex": self.scripts.get_ifindex(interface=ifname)
                        }]
                    }

            # Portchannel member
            if ifname in portchannel_members:
                ai, is_lacp = portchannel_members[ifname]
                iface["aggregated_interface"] = ai
                if is_lacp:
                    iface["enabled_protocols"] += ["LACP"]
            else:
                iface["subinterfaces"][0]["enabled_afi"] += ["BRIDGE"]
                if switchports[ifname][1]:
                    iface["subinterfaces"][0]["tagged_vlans"] = switchports[
                        ifname][1]
                if switchports[ifname][0]:
                    iface["subinterfaces"][0]["untagged_vlan"] = switchports[
                        ifname][0]
            interfaces += [iface]

            # GVRP
            rx_gvrp = re.compile(
                r"^" + ifname + "\s+Enabled\s+Normal\s+"
                r"Enabled\s+\d+\s+\d+\s+\d+",
                re.MULTILINE)
            match = rx_gvrp.search(gvrp)
            if match:
                iface["enabled_protocols"] += ["GVRP"]

            # LLDP
            rx_lldp = re.compile(
                r"^" + ifname + "\s+(Rx and Tx|Rx|Tx)\s+", re.MULTILINE)
            match = rx_lldp.search(lldp)
            if match:
                iface["enabled_protocols"] += ["LLDP"]

            # STP
            rx_stp = re.compile(
                r"^\s*" + ifname + "\s+enabled\s+\S+\s+\d+\s+"
                r"\S+\s+\S+\s+(Yes|No)\s+", re.MULTILINE)
            match = rx_stp.search(stp)
            if match:
                iface["enabled_protocols"] += ["STP"]

        return [{"interfaces": interfaces}]
