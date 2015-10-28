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
from noc.core.script.base import BaseScript
from noc.sa.interfaces import IGetInterfaceStatus


class Script(BaseScript):
    name = "HP.1905.get_interface_status"
    interface = IGetInterfaceStatus

    def execute(self, interface=None):
        r = []
        # Try SNMP first
        if self.has_snmp():
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
