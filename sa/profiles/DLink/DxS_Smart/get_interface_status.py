# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS_Smart.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus


class Script(BaseScript):
    name = "DLink.DxS_Smart.get_interface_status"
    interface = IGetInterfaceStatus

    def execute(self, interface=None):
        r = []
        # Try snmp first
        if self.has_snmp():
            try:
                for n, s in self.snmp.join_tables(
                        "1.3.6.1.2.1.31.1.1.1.1",
                        "1.3.6.1.2.1.2.2.1.8", bulk=True):  # IF-MIB
                    if n[:3] == 'Aux' or n[:4] == 'Vlan' \
                    or n[:11] == 'InLoopBack':
                        continue
                    if n[:6] == "Slot0/":
                        n = n[6:]
                    if interface:
                        if n == interface:
                            r += [{
                                "interface": n,
                                "status": int(s) == 1
                            }]
                    else:
                        r += [{
                            "interface": n,
                            "status": int(s) == 1
                        }]
                return r
            except self.snmp.TimeOutError:
                raise self.NotSupportedError()
        else:
            # Fallback to CLI
            ports = self.profile.get_ports(self, interface)
            for p in ports:
                if interface is not None:
                    if interface == p['port']:
                        return [{
                            "interface": interface,
                            "status": p['status']
                        }]
                        break
                else:
                    r += [{
                        "interface": p['port'],
                        "status": p['status']
                    }]
            return r
