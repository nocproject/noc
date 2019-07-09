# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IBM.NOS.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "IBM.NOS.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_mac = re.compile(r"^\s+(?P<mac>\S+)\s+(?P<vlan_id>\d+)\s+(?P<port>\S+)\s+(?P<state>\S+)\s+$")

    def execute_cli(self, interface=None, vlan=None, mac=None):
        cmd = "show mac-address-table"
        if mac is not None:
            cmd += " address %s" % self.profile.convert_mac(mac)
        if interface is not None:
            cmd += " interface port %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan
        try:
            v = self.cli(cmd)
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        r = []
        for match in self.rx_mac.finditer(v):
            if match:
                r += [
                    {
                        "vlan_id": match.group("vlan_id"),
                        "mac": match.group("mac"),
                        "interfaces": [match.group("port")],
                        "type": "D",
                    }
                ]
        return r
