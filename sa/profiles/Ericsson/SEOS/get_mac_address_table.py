# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Ericsson.MINI_LINK.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
from noc.core.text import parse_table
from noc.core.validators import is_int


class Script(BaseScript):
    name = "Ericsson.SEOS.get_mac_address_table"
    interface = IGetMACAddressTable

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = self.cli("show mac-address-table")
        # if mac is not None:
        #    cmd += " address %s" % mac
        if interface is not None:
            cmd += " port %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan
        r = []
        t = parse_table(cmd, footer="^show mac-address-table")
        for i in t:
            if is_int(i[0]):
                r += [
                    {
                        "vlan_id": i[0],
                        "mac": i[1],
                        "interfaces": [self.profile.convert_interface_name(i[4])],
                        "type": "D" if i[2] == "learned" else "S",
                    }
                ]
        return r
