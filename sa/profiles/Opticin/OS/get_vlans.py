# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Opticin.OS.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC Modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans


class Script(NOCScript):
    name = "Opticin.OS.get_vlans"
    cache = True
    implements = [IGetVlans]

    def execute(self):
        if self.snmp and self.access_profile.snmp_ro:
            # Try SNMP first
            try:
                oids = {}
                # Get OID -> VLAN ID mapping
                for oid, v in self.snmp.getnext("1.3.6.1.2.1.17.7.1.4.2.1.3",
                    bulk=True):  # dot1qVlanFdbId
                    oids[oid.split(".")[-1]] = v
                # Get VLAN names
                result = []
                for oid, v in self.snmp.getnext("1.3.6.1.2.1.17.7.1.4.3.1.1",
                    bulk=True):  # dot1qVlanStaticName
                    o = oid.split(".")[-1]
                    result += [{
                        "vlan_id":int(oids[o]),
                        "name":v.strip().rstrip('\x00')
                    }]
                return sorted(
                    result, lambda x, y: cmp(x["vlan_id"], y["vlan_id"])
                )
            except self.snmp.TimeOutError:
                # SNMP failed, continue with CLI
                pass
        ##
        ## Other
        ##
        else:
            rx_vlan_line = re.compile(
                r"^(?P<vlan_id>\d{1,4})\s+(?P<name>\S*\s+\S*)",
                re.IGNORECASE | re.DOTALL | re.MULTILINE)
            vlans = self.cli("show vlan")
            return [{
                "vlan_id": int(match.group("vlan_id")),
                "name": match.group("name")
            } for match in rx_vlan_line.finditer(vlans)]
