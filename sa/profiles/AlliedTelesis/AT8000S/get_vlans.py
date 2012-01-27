# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlliedTelesis.AT8000S.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## coded by azhur
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans
import re


class Script(NOCScript):
    name = "AlliedTelesis.AT8000S.get_vlans"
    implements = [IGetVlans]
    rx_vlan_line = re.compile(r"^(?P<vlan_id>\d{1,4})\s+(?P<name>\S+)\s")

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
                result = [{"vlan_id": 1, "name": "1"}]
                for oid, v in self.snmp.getnext("1.3.6.1.2.1.17.7.1.4.3.1.1",
                    bulk=True):  # dot1qVlanStaticName
                    o = oid.split(".")[-1]
                    result += [{"vlan_id": int(oids[o]), "name": v.strip()}]
                return sorted(result, lambda x, y: cmp(x["vlan_id"],
                     y["vlan_id"]))
            except self.snmp.TimeOutError:
                # SNMP failed, continue with CLI
                pass
        vlans = self.cli("show vlan")
        r = []
        for l in vlans.split("\n"):
            match = self.rx_vlan_line.match(l.strip())
            if match:
                name = match.group("name")
                vlan_id = int(match.group("vlan_id"))
                r.append({
                    "vlan_id": match.group("vlan_id"),
                    "name": match.group("name")
                    })
        return r
