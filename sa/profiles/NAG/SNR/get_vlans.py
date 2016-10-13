# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NAG.SNR.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "NAG.SNR.get_vlans"
    interface = IGetVlans

    def execute(self):
        r = []
        # Try snmp first
        if self.has_snmp():
            try:
                for vlan, name in self.snmp.join_tables("1.3.6.1.2.1.17.7.1.4.2.1.3",
                                                        "1.3.6.1.2.1.17.7.1.4.3.1.1"):
                    r.append({
                        "vlan_id": vlan,
                        "name": name
                        })
                return r
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        raise Exception("Not implemented")
