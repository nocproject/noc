# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.DSLAM.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "Eltex.DSLAM.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_mac = re.compile("(?P<mac>\S{17}) \[(?P<interface>.{4})\]")

    def execute(self, interface=None, vlan=None, mac=None):
        r = []
        cmd = self.cli("switch show mac table all")
        for match in self.rx_mac.finditer(cmd):
            interface = match.group("interface").strip()
            if interface == "cpu":
                mtype = "C"
            else:
                mtype = "D"
            r += [{
                "vlan_id": 1,
                "mac": match.group("mac"),
                "interfaces": [interface],
                "type": mtype
            }]
        return r
