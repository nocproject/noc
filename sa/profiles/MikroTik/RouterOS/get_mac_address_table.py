# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MikroTik.RouterOS.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "MikroTik.RouterOS.get_mac_address_table"
    interface = IGetMACAddressTable

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "/interface ethernet switch host print detail without-paging where dynamic"
        if mac is not None:
            cmd += " mac-address=%s" % mac
        if interface is not None:
            cmd += " ports=%s" % interface
        if vlan is not None:
            cmd += " vlan-id=%d" % vlan
        try:
            v = self.cli_detail(cmd)
        except self.CLISyntaxError:
            return []

        return [{
            "vlan_id": r["vlan-id"],
            "mac": r["mac-address"],
            "interfaces": [r["ports"]],
            "type": "D"
        } for n, f, r in v]
