# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Juniper.JUNOS.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
import re


class Script(BaseScript):
    name = "Juniper.JUNOS.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(
        r"(?P<vlan_name>[^ ]+)\s+(?P<mac>[^ ]+)\s+(?P<type>Learn|Static)\s+"
        r"[^ ]+\s+(?P<interfaces>.*)$"
    )

    def execute(self, interface=None, vlan=None, mac=None):
        if (
            not self.is_switch or
            not self.profile.command_exist(self, "ethernet-switching")
        ):
            return []
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
                        "static": "S"
                    }[match.group("type").lower()],
                }]
        return r
