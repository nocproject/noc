# ---------------------------------------------------------------------
# Iskratel.MBAN.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "Iskratel.MBAN.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(
        r"^(Current MAC addresses\s+:)?\s*(?P<mac>\S+)\s+\-\s+(?P<interface>\S+)\s*\n",
        re.MULTILINE,
    )

    def execute(self, interface=None, vlan=None, mac=None):
        cpu_mac = self.scripts.get_chassis_id()[0]["first_chassis_mac"]
        cmd = "show bridge mactable"
        if interface is not None:
            cmd += " interface %s" % interface
        r = []
        for match in self.rx_line.finditer(self.cli(cmd)):
            if match.group("mac") == cpu_mac:
                mtype = "C"
            else:
                mtype = "D"
            r.append(
                {
                    "vlan_id": 1,
                    "mac": match.group("mac"),
                    "interfaces": [match.group("interface")],
                    "type": mtype,
                }
            )
        return r
