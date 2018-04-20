# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ----------------------------------------------------------------------
# Alcatel.OS62xx.get_mac_address_table
# ----------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
=======
##----------------------------------------------------------------------
## Alcatel.OS62xx.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetMACAddressTable
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.lib.text import parse_table
import re


<<<<<<< HEAD
class Script(BaseScript):
    name = "Alcatel.OS62xx.get_mac_address_table"
    interface = IGetMACAddressTable
=======
class Script(noc.sa.script.Script):
    name = "Alcatel.OS62xx.get_mac_address_table"
    implements = [IGetMACAddressTable]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show bridge address-table"
        if vlan:
            cmd += " vlan %d" % vlan
        if mac:
            cmd += " address %s" % mac
        if interface:
            if interface.lower().startswith("po"):
                cmd += " port-channel %s" % interface
            else:
                cmd += " ethernet %s" % interface
        r = []
        for v, m, port, type in parse_table(self.cli(cmd)):
            r += [{
                "vlan_id": v,
                "mac": m,
                "interfaces": [port],
                "type": {"dynamic": "D", "static": "S"}[type.lower()]
            }]
        return r
