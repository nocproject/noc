# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.SMB.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "Cisco.SMB.get_mac_address_table"
    interface = IGetMACAddressTable
    rx_line = re.compile(r"^\s*(?P<vlan_id>\d{1,4})\s+(?P<mac>\S+)\s+(?P<interfaces>\S+)\s+(?P<type>\S+)\s*$")
    ignored_interfaces = ("0")

    def is_ignored_interface(self, i):
        if i.lower() in self.ignored_interfaces:
            return True
        return False

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show mac address-table"
        if mac is not None:
            cmd += " address %s" % self.profile.convert_mac(mac)
        if interface is not None:
            cmd += " interface %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan
        try:
            macs = self.cli(cmd)
        except self.CLISyntaxError:
            cmd = cmd.replace("mac address-table", "mac-address-table")
            try:
                macs = self.cli(cmd)
            except self.CLISyntaxError:
                # Not supported at all
                raise self.NotSupportedError()
        r = []
        for l in macs.splitlines():
            l = l.strip()
            match = self.rx_line.match(l)
            if match:
                mac = match.group("mac")
                interfaces = [
                    i.strip() for i in match.group("interfaces").split(",")
                ]
                interfaces = [
                    i for i in interfaces
                    if not self.is_ignored_interface(i)
                ]
                if not interfaces:
                    continue
                m_type = {"dynamic": "D",
                          "static": "S"}.get(match.group("type").lower())
                if not m_type:
                    continue
                r += [{
                    "vlan_id": match.group("vlan_id"),
                    "mac": mac,
                    "interfaces": interfaces,
                    "type": m_type,
                }]
        return r
