# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.MES.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
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

    TIMEOUT = 240

    rx_sh_ip_int = re.compile(
           r"^(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})/\d+\s+(?P<interface>.+?)\s+(Static|Dinamic)\s+(disable|enable)\s+(No|Yes)\s+(Valid|Invalid)",
           re.IGNORECASE)
    rx_status = re.compile(
           r"^(?P<interface>\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(?P<oper_status>Up|Down)\s+\S+\s+\S+\s+$",
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
           "fa": "physical",    # FastEthernet
           "gi": "physical",    # GigabitEthernet
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
           "te": "physical",    # TenGigabitEthernet
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
        # Get portchannels
        portchannel_members = {}
        for pc in self.scripts.get_portchannel():
            i = pc["interface"]
            t = pc["type"] == "L"
            for m in pc["members"]:
                portchannel_members[m] = (i, t)
        # Get IP interfaces
        ipv4_interfaces = defaultdict(list)  # interface -> [ipv4 addresses]
        ipv6_interfaces = defaultdict(list)  # interface -> [ipv6 addresses]
        iface = self.cli("show ip interface")
        for match in self.rx_sh_ip_int.finditer(iface):
            ip = match.group("ip")
            if ":" in ip:
                ipv6_interfaces[c_iface] += [ip]
            else:
                ipv4_interfaces[c_iface] += [ip]
        #
        interfaces = []
        # Get OSPF interfaces
        ospfs = self.get_ospfint()

        mac = self.scripts.get_chassis_id()[0]["first_chassis_mac"]
        status = self.cli("show interface status")
        config = self.cli("show interface configuration")
        descr = self.cli("show interface description")
        for match in self.rx_status.finditer(status):
            ifname = match.group("interface")
            o_stat = match.group("oper_status").lower() == "up"

            rx_config = re.compile(
                r"^" + ifname + "\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(?P<admin_status>(Up|Down))\s+\S+\s+\S+",
                re.MULTILINE)
            match = rx_config.search(config)
            a_stat = match.group("admin_status").lower() == "up"

            iface = {
                "name": ifname,
                "admin_status": a_stat,
                "oper_status": o_stat,
                "type": self.types[ifname[:2]],
                }

            rx_descr = re.compile(
                r"^" + ifname + "\s+(?P<desc>\S+.+?)$", re.MULTILINE)
            match = rx_descr.search(descr)
            if match:
                iface["description"] = match.group("desc")

            iface["mac"] = mac

            # Portchannel member
            if ifname in portchannel_members:
                ai, is_lacp = portchannel_members[ifname]
                iface["aggregated_interface"] = ai
                if is_lacp:
                    iface["enabled_protocols"] = ["LACP"]

            iface["subinterfaces"] = []
            interfaces += [iface]

        return [{"interfaces": interfaces}]
