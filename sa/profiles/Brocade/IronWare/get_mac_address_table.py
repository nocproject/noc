# ---------------------------------------------------------------------
# Brocade.IronWare.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "Brocade.IronWare.get_mac_address_table"
    interface = IGetMACAddressTable

    dataline = re.compile(r"^[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4}")

    def parse_mac_table(self, s):
        """
        Parse MAC address table
        :param s:
        :return:
        """
        r = []
        for line in s.splitlines():
            if self.dataline.match(line):
                parts = line.split()
                r.append([parts[0], parts[1], parts[3]])
        return r

    def execute_cli(self, interface=None, vlan=None, mac=None):
        if vlan:
            vlans = [vlan]
        else:
            vlans = [r["vlan_id"] for r in self.scripts.get_vlans()]
        if mac:
            rmac = mac.replace(":", "").lower()
        r = []
        for v in vlans:
            for m, port, type in self.parse_mac_table(self.cli("show mac-address vlan %d" % v)):
                rrmac = m.replace(".", "").lower()
                if (not interface or port == interface) and (not mac or rmac == rrmac):
                    r += [{"vlan_id": v, "mac": m, "interfaces": [port], "type": type}]
        return r
