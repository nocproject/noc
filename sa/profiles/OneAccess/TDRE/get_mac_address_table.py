# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# OneAccess.TDRE.get_mac_address_table
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
    name = "OneAccess.TDRE.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(
        r"^\s+macAddress = (?P<mac>\S+)\s*\n"
        r"^\s+port = (?P<port>port\d)\s*\n"
        r"^\s+type = (?P<type>\S+)\s*\n",
        re.MULTILINE
    )

    def execute(self, interface=None, vlan=None, mac=None):
        r = []
        self.cli("SELGRP Status")
        for etherswitch in ["1", "2"]:
            c = self.cli(
                "GET ethernet%s/switchCache[]/" % etherswitch
            )
            for match in self.rx_line.finditer(c):
                if match.group("type") == "dynamic":
                    mtype = "D"
                else:
                    mtype = "S"
                mac = match.group("mac")
                found = False
                for m in r:
                    if mac == m["mac"]:
                        found = True
                        break
                if not found:
                    r += [{
                        "vlan_id": 1,  # XXX Can not get vlan id
                        "mac": match.group("mac"),
                        "interfaces": [match.group("port")],
                        "type": mtype
                    }]
        return r
