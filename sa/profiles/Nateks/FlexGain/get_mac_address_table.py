# ---------------------------------------------------------------------
# Nateks.FlexGain.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "Nateks.FlexGain.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(
        r"^\d+\s+(?P<interface>\S+)\s+v(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<type>\S+)",
        re.MULTILINE,
    )

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show fdb"
        if interface is not None:
            cmd += " grep %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan
        if mac is not None:
            cmd += " grep %s" % mac
        macs = self.cli(cmd)
        r = []
        for match in self.rx_line.finditer(macs):
            r += [
                {
                    "vlan_id": int(match.group("vlan_id")),
                    "mac": mac if mac else match.group("mac"),
                    "interfaces": [match.group("interface")],
                    "type": {"DYNAMIC": "D", "STATIC": "S"}[match.group("type")],
                }
            ]
        return r
