# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EdgeCore.ES.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetMACAddressTable


class Script(NOCScript):
    name = "EdgeCore.ES.get_mac_address_table"
    implements = [IGetMACAddressTable]

    # ES3526 mac-address-table
    rx_line1 = re.compile(r"^\s*(?P<interface>(Eth\s*\d+/\s*\S+)|(Trunk\s*\d+))\s+"
                          r"(?P<mac>\S+)\s+"
                          r"(?P<vlan_id>\d+)\s+"
                          r"(?P<type>\S+)(?:\s+Delete on.*?)?$", re.MULTILINE)
    # ES3526 mac-address-table vlan <vlan_id>
    rx_line2 = re.compile(r"^\s*(?P<vlan_id>\d+)\s+"
                          r"(?P<mac>\S+)\s+"
                          r"(?P<interface>(Eth\s*\d+/\s*\S+)|(Trunk\s*\d+))\s+"
                          r"(?P<type>\S+)(?:\s+Delete on.*?)?$", re.MULTILINE)
    # ES3526 mac-address-table address <mac>
    rx_line3 = re.compile(r"^\s*(?P<mac>\S+)\s+"
                          r"(?P<vlan_id>\d+)\s+"
                          r"(?P<interface>(Eth\s*\d+/\s*\S+)|(Trunk\s*\d+))\s+"
                          r"(?P<type>\S+)(?:\s+Delete on.*?)?$", re.MULTILINE)
    # ES4626 mac-address-table
    rx_line4 = re.compile(r"^(?P<vlan_id>\d+)\s+"
                          r"(?P<mac>\S+)\s+"
                          r"(?P<type>\S+)\s+(?:\S+)\s+"
                          r"(?P<interface>.+)$", re.MULTILINE)

    types = {
        "learned": "D",
        "learned-psec": "D",
        "permanent": "S",
        "permanent-psec": "S",
        "dynamic": "D",
        "static": "S",
        "learn": "D",
        "cpu": "S"
    }

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show mac-address-table"
        if mac is not None:
            cmd += " address %s" % self.profile.convert_mac(mac)
        if interface is not None:
            cmd += " interface %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan
        macs = self.cli(cmd)
        r = []
        rx = self.find_re([self.rx_line1, self.rx_line2,
                           self.rx_line3, self.rx_line4], macs)
        for match in rx.finditer(macs):
            v = match.groupdict()
            r += [{
                "vlan_id": v["vlan_id"],
                "mac": v["mac"],
                "interfaces": [v["interface"]],
                "type": self.types[v["type"].lower()]
            }]
        return r
