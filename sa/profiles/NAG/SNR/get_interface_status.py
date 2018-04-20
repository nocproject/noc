# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# NAG.SNR.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import time
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus


class Script(BaseScript):
    name = "NAG.SNR.get_interface_status"
    interface = IGetInterfaceStatus
=======
##----------------------------------------------------------------------
## NAG.SNR.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import time
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetInterfaceStatus


class Script(noc.sa.script.Script):
    name = "NAG.SNR.get_interface_status"
    implements = [IGetInterfaceStatus]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self, interface=None):
        r = []
        # Try SNMP first
<<<<<<< HEAD
        if self.has_snmp():
            try:
                for n, s in self.snmp.join_tables("1.3.6.1.2.1.31.1.1.1.1",
                                                  "1.3.6.1.2.1.2.2.1.8"):  # IF-MIB
=======
        if self.snmp and self.access_profile.snmp_ro:
            try:
                for n, s in self.snmp.join_tables("1.3.6.1.2.1.31.1.1.1.1",
                    "1.3.6.1.2.1.2.2.1.8", bulk=True):  # IF-MIB
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                    if n[:8] == 'Ethernet':
                        pass
                    else:
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
