# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# DLink.DxS_Smart.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus


class Script(BaseScript):
    name = "DLink.DxS_Smart.get_interface_status"
    interface = IGetInterfaceStatus
=======
##----------------------------------------------------------------------
## DLink.DxS_Smart.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaceStatus


class Script(NOCScript):
    name = "DLink.DxS_Smart.get_interface_status"
    implements = [IGetInterfaceStatus]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self, interface=None):
        r = []
        # Try snmp first
<<<<<<< HEAD
        if self.has_snmp():
            try:
                for n, s in self.snmp.join_tables(
                        "1.3.6.1.2.1.31.1.1.1.1",
                        "1.3.6.1.2.1.2.2.1.8"):  # IF-MIB
=======
        if self.snmp and self.access_profile.snmp_ro:
            try:
                for n, s in self.snmp.join_tables(
                        "1.3.6.1.2.1.31.1.1.1.1",
                        "1.3.6.1.2.1.2.2.1.8", bulk=True):  # IF-MIB
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
