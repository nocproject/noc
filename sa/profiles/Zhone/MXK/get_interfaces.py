# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Zhone.MXK.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.mac import MAC


class Script(BaseScript):
    name = "Zhone.MXK.get_interfaces"
    interface = IGetInterfaces

    rx_ifbase = re.compile(r"^(\d+-\S+-\d+-\d+)/\S+$", re.MULTILINE)
    rx_ifbase1 = re.compile(r"^(\d+/\S+/\d+/\d+)/\S+$", re.MULTILINE)
    rx_mac = re.compile(
        r"^\s*MAC Address are enabled for (?P<count>\d+) address\(es\) starting at:\s*\n"
        r"^\s*(?P<mac>\S+)",
        re.MULTILINE,
    )
    rx_ether = re.compile(r"^ether\s+(?P<name>1-a-\d+-0/eth)\s*\n", re.MULTILINE)
    rx_ether_count = re.compile(r"^(?P<count>\d+) entries found.", re.MULTILINE)
    rx_ether_status = re.compile(
        r"^\s*Line Type-+> ETHERNET \(7\)\s*\n"
        r"^\s*GroupId -+> \d+\s*\n"
        r"^\s*Status -+> (?P<status>.+?)\s*\n"
        r"^\s*Redundancy .+\n"
        r"^\s*TxClk .+\n"
        r"^\s*RefClkSrc .+\n"
        r"^\s*If_index -+> (?P<snmp_ifindex>\d+)\s*\n"
        r"^\s*Physical -+> (?P<ifname>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_olt_status = re.compile(
        r"^\s*Line Type-+> OLT \(17\)\s*\n"
        r"^\s*GroupId -+> \d+\s*\n"
        r"^\s*Status -+> (?P<status>.+?)\s*\n"
        r"^\s*Redundancy .+\n"
        r"^\s*TxClk .+\n"
        r"^\s*RefClkSrc .+\n"
        r"^\s*If_index -+> (?P<snmp_ifindex>\d+)\s*\n"
        r"^\s*Physical -+> (?P<ifname>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_slot = re.compile(
        r"^\s*(?P<slot_no>\d+): MXK (?P<port_count>\d+) PORT (?P<port_type>\S+) \(RUNNING\)\s*\n",
        re.MULTILINE,
    )
    rx_ip = re.compile(
        r"^(?P<name>\S+)\s+UP\s+(?P<rd>\d+)\s+(?P<ip>\d+\S+)\s+(?P<mac>\S+)\s+(?P<alias>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_vlan_ipobridge = re.compile(r"^ipobridge-(?P<vlan_id>\d+)", re.MULTILINE)

    def execute_cli(self):
        interfaces = []
        mac = ""
        v = self.cli("eeshow card a", cached=True)
        match = self.rx_mac.search(v)
        start_mac = match.group("mac")
        count_mac = match.group("count")
        v = self.cli("list ether")
        match = self.rx_ether_count.search(v)
        if int(count_mac) != int(match.group("count")):
            raise self.CLIOperationError()
        ifcount = 0
        v = self.cli("showlinestatus 1 a")
        for match in self.rx_ether_status.finditer(v):
            ifname = self.rx_ifbase1.search(match.group("ifname")).group(1)
            mac = MAC(int(MAC(start_mac)) + ifcount)
            ifcount = ifcount + 1
            admin_status = match.group("status") != "ADMIN DOWN (3)"
            oper_status = match.group("status") == "ACTIVE (1)"
            iface = {
                "name": ifname,
                "type": "physical",
                "admin_status": admin_status,
                "oper_status": oper_status,
                "mac": mac,
                "snmp_ifindex": match.group("snmp_ifindex"),
                "subinterfaces": [
                    {
                        "name": match.group("ifname"),
                        "admin_status": admin_status,
                        "oper_status": oper_status,
                        "enabled_afi": ["BRIDGE"],
                        "mac": mac,
                        "snmp_ifindex": match.group("snmp_ifindex"),
                    }
                ],
            }
            interfaces += [iface]
        v = self.cli("interface show")
        for match in self.rx_ip.finditer(v):
            ifname = self.rx_ifbase1.search(match.group("name")).group(1)
            for i in interfaces:
                if i["name"] == ifname:
                    sub = {
                        "name": match.group("alias"),
                        "oper_status": True,
                        "admin_status": True,
                        "description": match.group("name"),
                        "mac": match.group("mac"),
                        "enable_afi": ["IPv4"],
                        "ip_addresess": [match.group("ip")],
                    }
                    match1 = self.rx_vlan_ipobridge.search(match.group("alias"))
                    if match1:
                        sub["vlan_ids"] = int(match1.group("vlan_id"))
                    i["subinterfaces"] += [sub]
                    break
        v = self.cli("slots", cached=True)
        for match in self.rx_slot.finditer(v):
            slot_no = match.group("slot_no")
            port_count = match.group("port_count")
            port_type = match.group("port_type")
            if port_type not in ["GPON"]:
                continue
            for port in range(1, int(port_count)):
                c = self.cli("showlinestatus %s %s" % (slot_no, port))
                if port_type == "GPON":
                    for match1 in self.rx_olt_status.finditer(c):
                        ifname = self.rx_ifbase1.search(match1.group("ifname")).group(1)
                        admin_status = match1.group("status") != "ADMIN DOWN (3)"
                        oper_status = match1.group("status") == "ACTIVE (1)"
                        iface = {
                            "name": ifname,
                            "type": "physical",
                            "admin_status": admin_status,
                            "oper_status": oper_status,
                            "snmp_ifindex": match1.group("snmp_ifindex"),
                            "subinterfaces": [
                                {
                                    "name": match1.group("ifname"),
                                    "admin_status": admin_status,
                                    "oper_status": oper_status,
                                    "enabled_afi": ["BRIDGE"],
                                    "snmp_ifindex": match1.group("snmp_ifindex"),
                                }
                            ],
                        }
                        interfaces += [iface]

        return [{"interfaces": interfaces}]
