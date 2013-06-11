# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.1905.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans


class Script(NOCScript):
    name = "HP.1905.get_vlans"
    implements = [IGetVlans]

    def execute(self):
        r = []
        # Try snmp first
        if self.snmp and self.access_profile.snmp_ro:
            try:
                for vlan, name in self.snmp.join_tables(
                    "1.3.6.1.2.1.17.7.1.4.2.1.3", "1.3.6.1.2.1.17.7.1.4.3.1.1",
                    bulk=True):
                    r.append({
                        "vlan_id": vlan,
                        "name": name
                        })
                return r
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        raise Exception("Not implemented")
