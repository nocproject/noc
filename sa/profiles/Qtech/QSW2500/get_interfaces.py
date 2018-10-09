# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QSW2500.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.lib.text import ranges_to_list
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "Qtech.QSW2500.get_interfaces"
    cache = True
    interface = IGetInterfaces

    rx_port = re.compile(
        "^\s*(?P<port>\d+)\s*(?P<admin_status>enable|disable)\s+"
        r"(?P<oper_status>up|down)", re.MULTILINE)
    rx_vlan = re.compile(
        r"^Port: (?P<port>\d+)\s*\n"
        r"^Administrative Mode:.+\n"
        r"^Operational Mode: (?P<op_mode>\S+)\s*\n"
        r"^Access Mode VLAN:\s*(?P<access_vlan>\d+)\s*\n"
        r"^Administrative Access Egress VLANs:.*\n"
        r"^Operational Access Egress VLANs:.*\n"
        r"^Trunk Native Mode VLAN:\s*(?P<trunk_native_vlan>.*)\n"
        r"^Administrative Trunk Allowed VLANs:.*\n"
        r"^Operational Trunk Allowed VLANs:\s*(?P<op_vlans>.*)\n"
        r"^Administrative Trunk Untagged VLANs:.*\n"
        r"^Operational Trunk Untagged VLANs:\s*(?P<op_untagged>.*)\n",
        re.MULTILINE
    )
    rx_descr = re.compile(r"^\s*(?P<port>\d+)\s*(?P<descr>.+)\n", re.MULTILINE)
    rx_ip_iface = re.compile(
        r"^\s*(?P<iface>\d+)\s+(?P<ip>\d\S+)\s+(?P<mask>\d\S+)\s+"
        r"(?P<vlan_id>\d+)", re.MULTILINE)

    def execute_cli(self):
        interfaces = []
        v = self.cli("show interface port")
        for match in self.rx_port.finditer(v):
            i = {
                "name": match.group("port"),
                "type": "physical",
                "admin_status": match.group("admin_status") == "enable",
                "oper_status": match.group("admin_status") == "up",
                "snmp_ifindex": int(match.group("port")),
                "subinterfaces": [{
                    "name": match.group("port"),
                    "admin_status": match.group("admin_status") == "enable",
                    "oper_status": match.group("admin_status") == "up",
                    "enabled_afi": ['BRIDGE']
                }]
            }
            interfaces += [i]
        v = self.cli("show interface port switchport")
        for match in self.rx_vlan.finditer(v):
            port = match.group("port")
            for iface in interfaces:
                if iface["name"] == port:
                    sub = iface["subinterfaces"][0]
                    if match.group("op_mode") in ["trunk", "hybrid"]:
                        sub["untagged_vlan"] = int(match.group("trunk_native_vlan"))
                        sub["tagged_vlans"] = ranges_to_list(match.group("op_vlans"))
                    else:
                        sub["untagged_vlan"] = int(match.group("access_vlan"))
                    break
        v = self.cli("show interface port description")
        for match in self.rx_descr.finditer(v):
            port = match.group("port")
            descr = match.group("descr").strip()
            if not descr:
                continue
            for iface in interfaces:
                if iface["name"] == port:
                    iface["description"] = descr
                    iface["subinterfaces"][0]["description"] = descr
                    break
        mac = self.scripts.get_chassis_id()[0]["first_chassis_mac"]
        v = self.cli("show interface ip")
        for match in self.rx_ip_iface.finditer(v):
            ifname = str(int(match.group("iface")) - 1)
            addr = match.group("ip")
            mask = match.group("mask")
            ip_address = "%s/%s" % (addr, IPv4.netmask_to_len(mask))
            i = {
                "name": "IP%s" % ifname,
                "type": "SVI",
                "mac": mac,
                "enabled_protocols": [],
                "subinterfaces": [{
                    "name": "ip%s" % ifname,
                    "mac": mac,
                    "enabled_afi": ['IPv4'],
                    "ipv4_addresses": [ip_address],
                    "vlan_ids": [match.group("vlan_id")]
                }]
            }
            interfaces += [i]
        return [{"interfaces": interfaces}]
