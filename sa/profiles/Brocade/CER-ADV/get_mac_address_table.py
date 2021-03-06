# ---------------------------------------------------------------------
# Brocade.CER-ADV.get_mac_address_table
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
    """
    Brocade.CER-ADV.get_mac_address_table
    """

    name = "Brocade.CER-ADV.get_mac_address_table"
    interface = IGetMACAddressTable
    dataline = re.compile("^[0-9a-f]{4}\\.[0-9a-f]{4}\\.[0-9a-f]{4}")

    def parse_mac_table(self, s):
        """
        Parse MAC address table
        :param s:
        :return:
        """
        r = []
        for line in s.splitlines():
            if self.dataline.match(line):
                ln = line.split()
                r.append([ln[0], ln[1], ln[3]])
        return r

    def execute(self, interface=None, vlan=None, mac=None):
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
