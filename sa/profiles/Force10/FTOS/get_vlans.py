# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
# Force10.FTOS.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVlans
from noc.lib.text import parse_table
import re


class Script(noc.sa.script.Script):
    name = "Force10.FTOS.get_vlans"
    implements = [IGetVlans]

    def execute(self):
        if self.snmp and self.access_profile.snmp_ro:
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
                    result += [{"vlan_id": int(oids[o]), "name":v.strip()}]
                return sorted(result, lambda x, y: cmp(x["vlan_id"], y["vlan_id"]))
            except self.snmp.TimeOutError:
                # SNMP failed, continue with CLI
                pass
        return [{
            "vlan_id": x[0],
            "name":x[1]
        } for x in parse_table(self.cli("show vlan brief"))]
