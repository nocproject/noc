# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
import re

rx_vrp3line = re.compile(r"^(?P<mac>\S+)\s+(?P<vlan_id>\d+)\s+(?P<type>Learned|Config static)\s+(?P<interfaces>[^ ]+)\s{2,}")
rx_vrp5line = re.compile(r"^(?P<mac>\S+)\s+(?P<vlan_id>\d+)(?:\s+|/)\-\s+(?:\-\s+)?(?P<interfaces>\S+)\s+(?P<type>dynamic|static|security)(?:\s+\-)?")
rx_vrp53line = re.compile(r"^(?P<mac>\S+)\s+(?P<vlan_id>\d+)\s+(?P<interfaces>\S+)\s+(?P<type>dynamic|static|security)\s+")


class Script(BaseScript):
    name = "Huawei.VRP.get_mac_address_table"
    interface = IGetMACAddressTable

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "display mac-address"
        if mac is not None:
            cmd += " %s" % self.profile.convert_mac(mac)
        version = self.scripts.get_version()["version"].split(".")[0]
        if version == "3":
            rx_line = rx_vrp3line
        elif self.match_version(version__startswith="5.3"):
            rx_line = rx_vrp53line
        elif version == "5":
            rx_line = rx_vrp5line
        r = []
        for l in self.cli(cmd).splitlines():
            match = rx_line.match(l.strip())
            if match:
                if vlan is not None and int(match.group("vlan_id")) != vlan:
                    continue
                if interface is not None and match.group("interfaces") != interface:
                    continue
                r.append({
                    "vlan_id": match.group("vlan_id"),
                    "mac": match.group("mac"),
                    "interfaces": [match.group("interfaces")],
                    "type": {
                        "dynamic": "D", "static": "S", "learned": "D",
                        "Config static": "S", "security": "S"
                    }[match.group("type").lower()],
                })
        return r
