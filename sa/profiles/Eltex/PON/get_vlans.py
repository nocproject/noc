# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.PON.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans


class Script(NOCScript):
    name = "Eltex.PON.get_vlans"
    implements = [IGetVlans]

    rx_vlan = re.compile(
        r"^(?P<vlan>\d+)\s+(?P<name>\S+)", re.MULTILINE)

    def execute(self):
        r = []
        # Try snmp first
        if self.snmp and self.access_profile.snmp_ro:
            try:
                for vlan, name in self.snmp.join_tables(
                    "1.3.6.1.2.1.17.7.1.4.3.1.5", "1.3.6.1.2.1.17.7.1.4.3.1.1",
                    bulk=True):
                    r.append({
                        "vlan_id": vlan,
                        "name": name
                        })
                return r
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        with self.profile.switch(self):
            for match in self.rx_vlan.finditer(self.cli("show vlan\r")):
                r.append({
                    "vlan_id": int(match.group("vlan")),
                    "name": match.group("name")
                    })
        return r
