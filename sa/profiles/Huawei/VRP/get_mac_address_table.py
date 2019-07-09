# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.VRP.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
import re


class Script(BaseScript):
    name = "Huawei.VRP.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_vrp3line = re.compile(
        r"^(?P<mac>\S+)\s+(?P<vlan_id>\d+)\s+(?P<type>Learned|Config static)\s+(?P<interfaces>[^ ]+)\s{2,}"
    )
    rx_vrp5line = re.compile(
        r"^(?P<mac>\S+)\s+(?P<vlan_id>\d+)(?:\s+|/)\-\s+(?:\-\s+)?(?P<interfaces>\S+)\s+"
        r"(?P<type>dynamic|static|security)(?:\s+\-)?"
    )
    rx_vrp5_bd_line = re.compile(
        r"^(?P<mac>\S+)\s+(?P<vlan_id>\d+)/\-/\-\s+(?P<interfaces>\S+)\s+(?P<type>dynamic|static|security)"
    )
    rx_vrp53line = re.compile(
        r"^(?P<mac>\S+)\s+(?P<vlan_id>\d+)\s+(?P<interfaces>\S+)\s+(?P<type>dynamic|static|security)\s+"
    )

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "display mac-address"
        if mac is not None:
            cmd += " %s" % self.profile.convert_mac(mac)
        v = self.cli(cmd)
        version = self.profile.fix_version(self.scripts.get_version())
        if version.startswith("3"):
            rx_line = self.rx_vrp3line
        elif version.startswith("5.3"):
            rx_line = self.rx_vrp53line
        elif version.startswith("5"):
            # Found in S5720S-52X-SI-AC v 5.170 (V200R011C10SPC600)
            if "VLAN/VSI/BD" in v:
                rx_line = self.rx_vrp5_bd_line
            else:
                rx_line = self.rx_vrp5line
        else:
            rx_line = self.rx_vrp5line
        r = []
        for line in v.splitlines():
            match = rx_line.match(line.strip())
            if match:
                if vlan is not None and int(match.group("vlan_id")) != vlan:
                    continue
                if interface is not None and match.group("interfaces") != interface:
                    continue
                r += [
                    {
                        "vlan_id": match.group("vlan_id"),
                        "mac": match.group("mac"),
                        "interfaces": [match.group("interfaces")],
                        "type": {
                            "dynamic": "D",
                            "static": "S",
                            "learned": "D",
                            "config static": "S",
                            "security": "S",
                        }[match.group("type").lower()],
                    }
                ]
        return r
