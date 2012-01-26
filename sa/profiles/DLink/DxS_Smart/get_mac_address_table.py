# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS_Smart.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetMACAddressTable
import re


class Script(NOCScript):
    name = "DLink.DxS_Smart.get_mac_address_table"
    implements = [IGetMACAddressTable]
    rx_line = re.compile(r"(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<type>Learnt|Static)\s+(?P<interfaces>\S+)", re.MULTILINE)

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "debug info"
        r = []
        for match in self.rx_line.finditer(self.cli(cmd)):
            m_interface = match.group("interfaces")
            m_vlan = match.group("vlan_id")
            m_mac = match.group("mac")
            if ((interface is None and vlan is None and mac is None) \
            or (interface is not None and interface == m_interface) \
            or (vlan is not None and vlan == m_vlan) \
            or (mac is not None and mac == m_mac)):
                r += [{
                    "vlan_id": m_vlan,
                    "mac": m_mac,
                    "interfaces": [m_interface],
                    "type": {"Learnt":"D", "Static":"S"}[match.group("type")]
                }]
        return r
