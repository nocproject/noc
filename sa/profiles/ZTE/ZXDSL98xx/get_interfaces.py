# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ZTE.ZXDSL98xx.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import copy
from collections import defaultdict
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "ZTE.ZXDSL98xx.get_interfaces"
    interface = IGetInterfaces

    rx_ip = re.compile(
        r"^-{70,}\s*\n"
        r"(?P<subs>(^\s+\d+\S+\s+\d+\S+\s+\d+\s+active\s*\n)+)"
        r"^\s*\n"
        r"^In band\s*\n"
        r"^-------\s*\n"
        r"^MAC address\s+: (?P<inband_mac>\S+)\s*\n"
        r"^\s*\n"
        r"^Out of band\s*\n"
        r"^-----------\s*\n"
        r"^IP address\s+: (?P<ip>\S+)\s*\n"
        r"^Netmask\s+: (?P<mask>\S+)\s*\n"
        r"^MAC address\s+: (?P<outband_mac>\S+)\s*\n",
        re.MULTILINE
    )
    rx_sub = re.compile(
        r"^\s+(?P<ip>\d+\S+)\s+(?P<mask>\d+\S+)\s+(?P<vlan_id>\d+)",
        re.MULTILINE
    )
    rx_card = re.compile(
        r"^(?P<slot>\d+)\s+\S+\s+\S+\s+\S+\s+(?P<ports>\d+)\s+\S+\s*\n",
        re.MULTILINE
    )
    rx_ethernet = re.compile(
        r"^Interface\s+: .+\n"
        r"^name\s+: .+\n"
        r"^Pvid\s+: (?P<pvid>\d+)\s*\n"
        r"^AdminStatus\s+: (?P<admin_status>\S+)\s+LinkStatus\(Eth\)\s+: (?P<oper_status>\S+)\s*\n"
        r"^ifType\s+: Ethernet\s+.+\n"
        r"^ifMtu\s+: (?P<mtu>\d+)\s+.+\n",
        re.MULTILINE
    )
    # Do not optimize this.
    rx_adsl = re.compile(
        r"^Interface\s+: .+\n"
        r"^name\s+: .+\n"
        r"Pvid PVC1\s+: (?P<pvid1>\d+)\s+Pvid PVC2\s+: (?P<pvid2>\d+)\s*\n"
        r"Pvid PVC3\s+: (?P<pvid3>\d+)\s+Pvid PVC4\s+: (?P<pvid4>\d+)\s*\n"
        r"Pvid PVC5\s+: (?P<pvid5>\d+)\s+Pvid PVC6\s+: (?P<pvid6>\d+)\s*\n"
        r"Pvid PVC7\s+: (?P<pvid7>\d+)\s+Pvid PVC8\s+: (?P<pvid8>\d+)\s*\n"
        r"^\s*\n"
        r"^AdminStatus\s+: (?P<admin_status>\S+)\s+LinkStatus\(ADSL\)\s+: (?P<oper_status>\S+)\s*\n"
        r"^ifType\s+: ADSL\s+ifMtu\s+: (?P<mtu>\d+)\s+.+\n",
        re.MULTILINE
    )
    # Do not optimize this.
    rx_pvc = re.compile(
        r"^\d+/\d+\s+PVC1\s+(?P<vpi1>\d+)\s+(?P<vci1>\d+).*\n"
        r"^\d+/\d+\s+PVC2\s+(?P<vpi2>\d+)\s+(?P<vci2>\d+).*\n"
        r"^\d+/\d+\s+PVC3\s+(?P<vpi3>\d+)\s+(?P<vci3>\d+).*\n"
        r"^\d+/\d+\s+PVC4\s+(?P<vpi4>\d+)\s+(?P<vci4>\d+).*\n"
        r"^\d+/\d+\s+PVC5\s+(?P<vpi5>\d+)\s+(?P<vci5>\d+).*\n"
        r"^\d+/\d+\s+PVC6\s+(?P<vpi6>\d+)\s+(?P<vci6>\d+).*\n"
        r"^\d+/\d+\s+PVC7\s+(?P<vpi7>\d+)\s+(?P<vci7>\d+).*\n"
        r"^\d+/\d+\s+PVC8\s+(?P<vpi8>\d+)\s+(?P<vci8>\d+).*\n",
        re.MULTILINE
    )

    def execute(self):
        interfaces = []
        match = self.rx_ip.search(self.cli("show ip subnet"))
        i = {
            "name": "inband",
            "type": "SVI",
            "mac": match.group("inband_mac"),
            "subinterfaces": []
        }
        sub_number = 0
        for match1 in self.rx_sub.finditer(match.group("subs")):
            ip = match1.group("ip")
            mask = match1.group("mask")
            ip_address = "%s/%s" % (ip, IPv4.netmask_to_len(mask))
            sub = {
                "name": "inband%s" % sub_number,
                "enabled_afi": ["IPv4"],
                "ipv4_addresses": [ip_address],
                "vlan_ids": [match1.group("vlan_id")]

            }
            sub_number = sub_number + 1
            i["subinterfaces"] += [sub]
        interfaces += [i]
        ip = match.group("ip")
        mask = match.group("mask")
        ip_address = "%s/%s" % (ip, IPv4.netmask_to_len(mask))
        i = {
            "name": "outb",
            "type": "SVI",
            "mac": match.group("outband_mac"),
            "subinterfaces": [{
                "name": "outband",
                "enabled_afi": ["IPv4"],
                "ipv4_addresses": [ip_address],
            }]
        }
        interfaces += [i]
        for match in self.rx_card.finditer(self.cli("show card")):
            slot = match.group("slot")
            ports = match.group("ports")
            if ports == 0:
                continue
            for port_n in range(int(ports)):
                ifname = "%s/%s" % (slot, port_n+1)
                try:
                    v = self.cli("show interface %s" % ifname)
                except self.CLISyntaxError:
                    continue
                match = self.rx_ethernet.search(v)
                if match:
                    i = {
                        "name": ifname,
                        "type": "physical",
                        "admin_status": match.group("admin_status") == "enable",
                        "oper_status": match.group("oper_status") == "up",
                        "subinterfaces": [{
                            "name": ifname,
                            "enabled_afi": ["BRIDGE"],
                            "mtu": match.group("mtu"),
                            "admin_status": match.group("admin_status") == "enable",
                            "oper_status": match.group("oper_status") == "up",
                        }]
                    }
                    interfaces += [i]
                match = self.rx_adsl.search(v)
                if match:
                    i = {
                        "name": ifname,
                        "type": "physical",
                        "admin_status": match.group("admin_status") == "enable",
                        "oper_status": match.group("oper_status") == "up",
                        "subinterfaces": []
                    }
                    v = self.cli("show atm pvc interface %s" % ifname)
                    match1 = self.rx_pvc.search(v)
                    i["subinterfaces"] = [{
                        "name": "%s/%s" % (ifname, "1"),
                        "enabled_afi": ["BRIDGE", "ATM"],
                        "mtu": match.group("mtu"),
                        "vlan_ids": [match.group("pvid1")],
                        "vpi": match1.group("vpi1"),
                        "vci": match1.group("vci1")
                    },{
                        "name": "%s/%s" % (ifname, "2"),
                        "enabled_afi": ["BRIDGE", "ATM"],
                        "mtu": match.group("mtu"),
                        "vlan_ids": [match.group("pvid2")],
                        "vpi": match1.group("vpi2"),
                        "vci": match1.group("vci2")
                    },{
                        "name": "%s/%s" % (ifname, "3"),
                        "enabled_afi": ["BRIDGE", "ATM"],
                        "mtu": match.group("mtu"),
                        "vlan_ids": [match.group("pvid3")],
                        "vpi": match1.group("vpi3"),
                        "vci": match1.group("vci3")
                    },{
                        "name": "%s/%s" % (ifname, "4"),
                        "enabled_afi": ["BRIDGE", "ATM"],
                        "mtu": match.group("mtu"),
                        "vlan_ids": [match.group("pvid4")],
                        "vpi": match1.group("vpi4"),
                        "vci": match1.group("vci4")
                    },{
                        "name": "%s/%s" % (ifname, "5"),
                        "enabled_afi": ["BRIDGE", "ATM"],
                        "mtu": match.group("mtu"),
                        "vlan_ids": [match.group("pvid5")],
                        "vpi": match1.group("vpi5"),
                        "vci": match1.group("vci5")
                    },{
                        "name": "%s/%s" % (ifname, "6"),
                        "enabled_afi": ["BRIDGE", "ATM"],
                        "mtu": match.group("mtu"),
                        "vlan_ids": [match.group("pvid6")],
                        "vpi": match1.group("vpi6"),
                        "vci": match1.group("vci6")
                    },{
                        "name": "%s/%s" % (ifname, "7"),
                        "enabled_afi": ["BRIDGE", "ATM"],
                        "mtu": match.group("mtu"),
                        "vlan_ids": [match.group("pvid7")],
                        "vpi": match1.group("vpi7"),
                        "vci": match1.group("vci7")
                    },{
                        "name": "%s/%s" % (ifname, "8"),
                        "enabled_afi": ["BRIDGE", "ATM"],
                        "mtu": match.group("mtu"),
                        "vlan_ids": [match.group("pvid8")],
                        "vpi": match1.group("vpi8"),
                        "vci": match1.group("vci8")
                    }]
                    interfaces += [i]
        return [{"interfaces": interfaces}]
