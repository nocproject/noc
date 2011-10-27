# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.MES.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetMACAddressTable

rx_line = re.compile(r"^\s*(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<interfaces>\S+)\s+(?P<type>\S+)", re.MULTILINE)

class Script(noc.sa.script.Script):
    name = "Eltex.MES.get_mac_address_table"
    implements = [IGetMACAddressTable]

    def execute(self,interface=None,vlan=None,mac=None):
        cmd = "show mac address-table"
        if mac is not None:
            cmd += " address %s"%self.profile.convert_mac(mac)
        if interface is not None:
            cmd += " interface %s"%interface
        if vlan is not None:
            cmd += " vlan %s"%vlan
        r = []
        for match in rx_line.finditer(self.cli(cmd)):
                interfaces = match.group("interfaces")
                if interfaces == '0':
                    continue
                r.append( {
                    "vlan_id"   : match.group("vlan_id"),
                    "mac"       : match.group("mac"),
                    "interfaces": [interfaces],
                    "type"      : {"dynamic":"D","static":"S","permanent":"S","self":"S"}[match.group("type").lower()],
                } )
        return r
