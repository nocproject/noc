# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.1905.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import time
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetInterfaceStatus


class Script(noc.sa.script.Script):
    name = "HP.1905.get_interface_status"
    implements = [IGetInterfaceStatus]

    def execute(self, interface=None):
        r = []
        # Try SNMP first
        if self.snmp and self.access_profile.snmp_ro:
            try:
                for n, s in self.snmp.join_tables("1.3.6.1.2.1.31.1.1.1.1",
                    "1.3.6.1.2.1.2.2.1.8", bulk=True):  # IF-MIB
                    if n[:3] == 'Aux' or n[:4] == 'Vlan' \
                    or n[:10] == 'InLoopBack':
                        continue
                    if interface:
                        if n == interface:
                            r.append({
                                "interface": n,
                                "status": int(s) == 1
                                })
                    else:
                        r.append({
                            "interface": n,
                            "status": int(s) == 1
                            })
                return r
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        raise Exception("Not implemented")
