# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# BDCOM_xPON.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modules
from noc.core.ip import IPv4
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "BDCOM.xPON.get_interfaces"
    cache = True
    interface = IGetInterfaces
    TIMEOUT = 300

    rx_int1 = re.compile(
        r"(?P<ifname>^g\S+|epon\S+)(?:\s\s\s|\s)(?P<desc>(?:\S+|\s))\s+(?P<status>\S+)"
        r"(?:\s*\d+|\s*T\S+|\s)(?:\s*(?P<duplex>full|auto)|\s)(?:\s*auto|\s*\d+\S+|\s)"
        r"\s+(?P<type>\S+)",
        re.MULTILINE)

    rx_svi = re.compile(
        r"(?P<ifname>^VLAN\d+).+Address (?P<ip>\S+) mask (?P<mask>\S+)",
        re.MULTILINE | re.DOTALL)

    rx_lldp = re.compile(
        r"(?P<ifname>^\S+):\nRx: (?P<lldp_rx>\S+)\nTx: (?P<lldp_tx>\S+)",
    )

    types = {
        "GigaEthernet-TX": "physical",  # GigabitEthernet
        "GigaEthernet-FX": "physical",  # GigabitEthernet
        "Giga-Combo-FX": "physical",  # GigabitEthernet Combo port
        "GigaEthernet-PON": "physical",  # EPON port
        "GigaEthernet-LLID": "other",  # EPON port
        "Giga-TX": "physical",  # GigabitEthernet
        "Giga-FX": "physical",  # GigabitEthernet
        "Giga-PON": "physical",  # EPON port
        "Giga-LLID": "other"  # EPON port
    }

    # @todo: snmp
    # @todo: fix admin\open status
    # @todo: vlans
    # @todo: cdp
    # @todo: gvrp
    # @todo: mac

    def execute(self):
        ifaces = []
        tagged = []
        untag = ""
        v = self.cli("show interface brief")
        for match in self.rx_int1.finditer(v):
            ifname = self.profile.convert_interface_name(match.group("ifname"))
            typ = match.group('type')
            iftype = self.types[typ]
            i = {
                "name": ifname,
                "type": iftype,
                "admin_status": "up" in match.group('status'),
                "oper_status": "up" in match.group('status'),
                "description": match.group('desc'),
                "enabled_protocols": [],
                "subinterfaces": [{
                    "name": ifname,
                    "admin_status": "up" in match.group('status'),
                    "oper_status": "up" in match.group('status'),
                    "description": match.group('desc'),
                    "tagged_vlans": tagged,
                    "untagged_vlan": untag,
                }]
            }
            if ifname.startswith('GigaEthernet'):
                cmd1 = "show lldp interface %s" % ifname
                cmd2 = self.cli(cmd1)
                for match1 in self.rx_lldp.finditer(cmd2):
                    if match1.group('lldp_rx') == "enabled" \
                            or match1.groups('lldp_tx') == "enabled":
                        i["enabled_protocols"] = ["LLDP"]
            ifaces += [i]
        match = self.rx_svi.search(self.cli("sh ip interface"))
        if match:
            vlan = match.group('ifname')
            vlan = vlan[4:]
            i = {
                "name": match.group('ifname'),
                "type": "SVI",
                "oper_status": True,
                "admin_status": True,
                "enabled_protocols": [],
                "subinterfaces": [{
                    "name": match.group('ifname'),
                    "oper_status": True,
                    "admin_status": True,
                    "vlan_ids": [int(vlan)],
                    "enabled_afi": ['IPv4']
                }]
            }
            addr = match.group("ip")
            mask = match.group("mask")
            ip_address = "%s/%s" % (addr, IPv4.netmask_to_len(mask))
            i['subinterfaces'][0]["ipv4_addresses"] = [ip_address]
            ifaces += [i]
        return [{"interfaces": ifaces}]
