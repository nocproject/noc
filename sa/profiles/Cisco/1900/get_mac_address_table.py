# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.1900.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
import noc.sa.profiles
from noc.sa.interfaces import IGetMACAddressTable
import re

rx_line = re.compile(
    r"^(?P<mac>\S+)\s+(?P<interface>\S+ \d\/\d+)\s+(?P<type>\S+)\s+All")


class Script(noc.sa.script.Script):
    name = "Cisco.1900.get_mac_address_table"
    implements = [IGetMACAddressTable]

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show mac-address-table"
        if mac is not None:
            cmd += " address %s" % self.profile.convert_mac(mac)
        elif interface is not None:
            cmd += " interface %s" % interface
        vlans = self.cli(cmd)
        r = []
        running_config = self.cli("show running-config")
        for l in vlans.split("\n"):
            match = rx_line.match(l.strip())
            if match:
                vlan_id = "1"
                rx_cfg = re.compile(
                    "interface " + match.group("interface").replace("/", ".") +
                    ".+vlan-membership static (?P<static_vlan_id>\d+)",
                    re.DOTALL | re.MULTILINE)
                cfg_match = rx_cfg.search(running_config)
                if cfg_match:
                    vlan_id = cfg_match.group("static_vlan_id")
                if vlan is not None:
                    if int(vlan) != int(vlan_id):
                        continue
                m_type = {"dynamic": "D",
                          "permanent": "S"}.get(match.group("type").lower())
                r.append({
                    "vlan_id": vlan_id,
                    "mac": match.group("mac"),
                    "interfaces": [match.group("interface")],
                    "type": m_type
                })

        return r
