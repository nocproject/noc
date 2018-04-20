# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Juniper.JUNOS.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
import re


class Script(BaseScript):
    name = "Juniper.JUNOS.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(
        r"(?P<vlan_name>[^ ]+)\s+(?P<mac>[^ ]+)\s+"
        r"(?P<type>Learn|Static|S|D|L|P)\s+"
        r"[^ ]+\s+(?P<interfaces>.*)$"
    )

    def execute(self, interface=None, vlan=None, mac=None):
        if (
            not self.is_switch or
            not self.profile.command_exist(self, "ethernet-switching")
        ):
            return []
=======
##----------------------------------------------------------------------
## Juniper.JUNOS.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetMACAddressTable, IGetVlans
import re

rx_line = re.compile(r"(?P<vlan_name>[^ ]+)\s+(?P<mac>[^ ]+)\s+(?P<type>Learn|Static)\s+[^ ]+\s+(?P<interfaces>.*)$", re.IGNORECASE)


class Script(noc.sa.script.Script):
    name = "Juniper.JUNOS.get_mac_address_table"
    implements = [IGetMACAddressTable]
    requires = [("get_vlans", IGetVlans)]

    def execute(self, interface=None, vlan=None, mac=None):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        r = []
        vlans = {}
        for v in self.scripts.get_vlans():
            vlans[v["name"]] = v["vlan_id"]
        cmd = "show ethernet-switching table"
        if mac is not None:
            cmd += " | match %s" % mac
        if interface is not None:
            cmd += " interface %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan
        for l in self.cli(cmd).splitlines():
<<<<<<< HEAD
            match = self.rx_line.match(l.strip())
            if match:
                if match.group("vlan_name") in vlans:
                    vlan_id = int(vlans[match.group("vlan_name")])
                else:
                    vlan_id = 1
                ifname = match.group("interfaces")
                if ifname.endswith(".0"):
                    ifname = ifname[:-2]
                r += [{
                    "vlan_id": vlan_id,
                    "mac": match.group("mac"),
                    "interfaces": [ifname],
                    "type": {
                        "learn": "D",
                        "static": "S",
                        "d": "D",  # dynamic
                        "s": "S",  # static
                        "l": "D",  # locally learned
                        "p": "S",  # Persistent static
                        # "se": "s",  # statistics enabled
                        # "nm": "s",  # non configured MAC
                        # "r": "s",  # remote PE MAC
                        # "o": "s"  # ovsdb MAC
                    }[match.group("type").lower()]
=======
            match = rx_line.match(l.strip())
            if match:
                vlan_id = int(vlans[match.group("vlan_name")])
                r += [{
                    "vlan_id": vlan_id,
                    "mac": match.group("mac"),
                    "interfaces": [match.group("interfaces")],
                    "type": {
                        "learn":"D",
                         "static":"S"
                    }[match.group("type").lower()],
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                }]
        return r
