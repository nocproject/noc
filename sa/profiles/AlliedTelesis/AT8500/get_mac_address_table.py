# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# AlliedTelesis.AT8500.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# coded by azhur
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
import re


class Script(BaseScript):
    name = "AlliedTelesis.AT8500.get_mac_address_table"
    interface = IGetMACAddressTable
    rx_line = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+(?P<mac>[:0-9a-fA-F]+)\s+"
        r"(?P<interfaces>\d+)\s+(?P<type>[\(\)\,\-\w\s]+)$")
=======
##----------------------------------------------------------------------
## AlliedTelesis.AT8500.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## coded by azhur
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetMACAddressTable
import re


class Script(NOCScript):
    name = "AlliedTelesis.AT8500.get_mac_address_table"
    implements = [IGetMACAddressTable]
    rx_line = re.compile(r"^\s*(?P<vlan_id>\d+)\s+(?P<mac>[:0-9a-fA-F]+)\s+(?P<interfaces>\d+)\s+(?P<type>[\(\)\,\-\w\s]+)$")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show switch fdb"
        if mac is not None:
            cmd += " address=%s" % mac
        if interface is not None:
            cmd += " port(s)=%s" % interface
        if vlan is not None:
            cmd += " vlan=%s" % vlan
        self.cli("terminal datadump")
        vlans = self.cli(cmd)
        vlans = self.strip_first_lines(vlans, 4)
        r = []
        for l in vlans.split("\n"):
            match = self.rx_line.match(l.strip())
            if match:
                r.append({
                    "vlan_id": match.group("vlan_id"),
                    "mac": match.group("mac"),
                    "interfaces": [match.group("interfaces")],
<<<<<<< HEAD
                    "type": {
                        "Dynamic": "D",
                        "Static": "S",
                        "Static (fixed,non-aging)": "S",
                        "Multicast": "M"
                    }[match.group("type")]
=======
                    "type": {"Dynamic": "D",
                        "Static": "S", "Static (fixed,non-aging)": "S",
                        "Multicast": "M"}[match.group("type")],
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                })
        return r
