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

class Script(noc.sa.script.Script):
    name = "Eltex.MES.get_mac_address_table"
    implements = [IGetMACAddressTable]

    rx_line = re.compile(r"^\s*(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<interfaces>\S+)\s+(?P<type>\S+)", re.MULTILINE)

    def execute(self, interface=None, vlan=None, mac=None):
        r = []
# BUG http://bt.nocproject.org/browse/NOC-36
        # Try snmp first
#        if self.snmp and self.access_profile.snmp_ro:
#            try:
#                for vlan, mac, interfaces, typ in self.snmp.join_tables("1.3.6.1.2.1.17.7.1.2.2.1.2", "1.3.6.1.2.1.17.4.3.1.1", "1.3.6.1.2.1.17.4.3.1.2", "1.3.6.1.2.1.17.4.3.1.3", bulk=True, cached=True): #
#                    r.append( {
#                        "vlan_id"   : vlan,
#                        "mac"       : mac,
#                        "interfaces": [interfaces],
#                        "type"      : {"3":"D","2":"S","1":"S"}[typ],
#                    } )
#                return r
#            except self.snmp.TimeOutError:
#                pass

        # Fallback to CLI
        cmd = "show mac address-table"
        if mac is not None:
            cmd += " address %s"%self.profile.convert_mac(mac)
        if interface is not None:
            cmd += " interface %s"%interface
        if vlan is not None:
            cmd += " vlan %s"%vlan
        for match in self.rx_line.finditer(self.cli(cmd)):
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
