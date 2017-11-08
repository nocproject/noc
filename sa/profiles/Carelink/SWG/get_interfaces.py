# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Carelink.SWG.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


import re

from noc.core.ip import IPv4
from noc.core.script.base import BaseScript
from noc.lib.text import parse_table
from noc.lib.validators import is_int
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "Carelink.SWG.get_interfaces"
    interface = IGetInterfaces

    rx_lldp = re.compile(r"^(?P<port>\d+)\s+Enabled", re.MULTILINE)
    rx_ctp = re.compile(r"^(?P<port>\d+)\s+\S+\s+Enabled", re.MULTILINE)
    rx_ipif = re.compile(
        r"^IP Address\s+: (?P<ip>\S+)\s*\n"
        r"^IP Mask\s+: (?P<mask>\S+)\s*\n"
        r"^IP Router\s+: .+\n"
        r"^DNS Server\s+: .+\n"
        r"^VLAN ID\s+: (?P<vlan_id>\d+)\s*\n",
        re.MULTILINE
    )

    def get_lldp(self):
        try:
            return self.rx_lldp.findall(self.cli("show lldp"))
        except self.CLISyntaxError:
            return []
        return []

    def get_ctp(self):
        try:
            v = self.cli("show loopback-detection config")
            if "Loop Protection  : Enabled" not in v:
                return []
        except self.CLISyntaxError:
            return []
        try:
            v = self.cli("show loopback-detection status")
            return self.rx_ctp.findall(v)
        except self.CLISyntaxError:
            return []
        return []

    def execute(self):
        interfaces = []
        lldp = self.get_lldp()
        ctp = self.get_ctp()
        for i in parse_table(self.cli("show interface  switchport")):
            iface = {
                "name": i[0],
                "type": "physical",
                "enabled_protocols": [],
                "subinterfaces": [{
                    "name": i[0],
                    "enabled_afi": ["BRIDGE"],
                    "untagged_vlan": i[1]
                }]
            }
            if i[0] in lldp:
                iface["enabled_protocols"] += ["LLDP"]
            if i[0] in ctp:
                iface["enabled_protocols"] += ["CTP"]
            interfaces += [iface]
        for v in parse_table(self.cli("show vlan"), max_width=80):
            if not is_int(v[0]):
                continue
            vlan_id = v[0]
            ports = self.expand_rangelist(v[2])
            for i in interfaces:
                if i["subinterfaces"][0]["untagged_vlan"] == vlan_id:
                    continue
                if (int(i["name"]) in ports):
                    if "tagged_vlans" in i["subinterfaces"][0]:
                        i["subinterfaces"][0]["tagged_vlans"] += [vlan_id]
                    else:
                        i["subinterfaces"][0]["tagged_vlans"] = [vlan_id]
        mac = self.scripts.get_chassis_id()[0]["first_chassis_mac"]
        match = self.rx_ipif.search(self.cli("show ip interface"))
        ip = match.group("ip")
        mask = match.group("mask")
        ip_address = "%s/%s" % (ip, IPv4.netmask_to_len(mask))
        iface = {
            "name": "mgmt",
            "type": "SVI",
            "mac": mac,
            "subinterfaces": [{
                "name": "mgmt",
                "enabled_afi": ["BRIDGE"],
                "vlan_ids": match.group("vlan_id"),
                "ipv4_addresses": [ip_address],
                "enabled_afi": ["IPv4"],
                "mac": mac
            }]
        }
        interfaces += [iface]
        return [{"interfaces": interfaces}]
