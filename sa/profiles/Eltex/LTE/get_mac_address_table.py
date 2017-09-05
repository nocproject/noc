# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.LTE.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "Eltex.LTE.get_mac_address_table"
    interface = IGetMACAddressTable
    cache = True

    rx_olt = re.compile(
        r"^(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<interface>(\S+ \d+|\S+))\s+"
        r"(?P<type>\S+)\s+\S+\s+\S+( to CPU)?\s+\d+\s*$", re.MULTILINE)

    rx_switch = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+\S+\s+(?P<mac>\S+)\s+(?P<type>\S+)\s+"
        r"(?P<interface>\d+|CPU)\s+", re.MULTILINE)

    def execute(self, interface=None, vlan=None, mac=None):
        r = []
        """
        I do not know, how parse this
        ----MAC table for OLT channel 0:----
          0) CONFIG Ch/ID: x/134    STATUS Ch/ID: 0/134    MAC: 02:00:22:00:14:B4  Port: uni0
        +0) C8:BE:19:B1:8B:F1
          1) CONFIG Ch/ID: x/134    STATUS Ch/ID: 0/134    MAC: 02:00:22:00:14:B4  Port: uni1
        +0) 00:07:67:99:AD:7B
          2) CONFIG Ch/ID: 0/20     STATUS Ch/ID: 0/20     MAC: 02:00:4D:01:80:B4  Port: uni0
        +0) A8:F9:4B:03:44:81
        +1) 1C:BB:A8:0F:25:3A
        +2) 00:02:9B:92:04:64
        # LTE ports
        cmd = "show mac table"
        if interface is not None:
            cmd += " %s" % interface
        else:
            cmd += " x"
        for match in self.rx_olt.finditer(self.cli(cmd)):
            interfaces = match.group("interfaces")
            if interfaces == '0':
                continue
            r.append({
                    "vlan_id": match.group("vlan_id"),
                    "mac": match.group("mac"),
                    "interfaces": [interfaces],
                    "type": {
                        "dynamic": "D",
                        "static": "S",
                        "permanent": "S",
                        "self": "S"
                        }[match.group("type").lower()],
                    })
        """
        # Switch ports
        cmd = "show mac"
        if vlan is not None:
            cmd += " include vlan %s" % vlan
        elif interface is not None:
            cmd += " include interface %s" % interface
        elif mac is not None:
            cmd += " include mac %s" % self.profile.convert_mac(mac)
        with self.profile.switch(self):
            c = self.cli(cmd, cached=True)
            for match in self.rx_switch.finditer(c):
                interface = match.group("interface")
                mtype = {
                    "dynamic": "D",
                    "static": "S",
                    "permanent": "S",
                    "self": "S"
                }[match.group("type").lower()]
                if interface == "CPU":
                    mtype = "C"
                r += [{
                    "vlan_id": match.group("vlan_id"),
                    "mac": match.group("mac"),
                    "interfaces": [interface],
                    "type": mtype
                }]
            if r:
                return r
            for match in self.rx_olt.finditer(c):
                interface = match.group("interface")
                mtype = {
                    "dynamic": "D",
                    "static": "S",
                    "permanent": "S",
                    "self": "S"
                }[match.group("type").lower()]
                if interface == "CPU":
                    mtype = "C"
                r += [{
                    "vlan_id": match.group("vlan_id"),
                    "mac": match.group("mac"),
                    "interfaces": [interface],
                    "type": mtype
                }]
        return r
