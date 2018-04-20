# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# DLink.DVG.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus


class Script(BaseScript):
    name = "DLink.DVG.get_interface_status"
    interface = IGetInterfaceStatus
=======
##----------------------------------------------------------------------
## DLink.DVG.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

import noc.sa.script
from noc.sa.interfaces import IGetInterfaceStatus


class Script(noc.sa.script.Script):
    name = "DLink.DVG.get_interface_status"
    implements = [IGetInterfaceStatus]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self, interface=None):
        r = []
        # Only one way: SNMP.
<<<<<<< HEAD
        if self.has_snmp():
            try:
                for i, n, s in self.snmp.join([
                    "1.3.6.1.2.1.2.2.1.2",
                    "1.3.6.1.2.1.2.2.1.8"
                ]):
=======
        if self.snmp and self.access_profile.snmp_ro:
            try:
                for n, s in self.snmp.join_tables("1.3.6.1.2.1.2.2.1.2",
                                                  "1.3.6.1.2.1.2.2.1.8",
                                                  bulk=True):  # IF-MIB
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                    if n[:3] == 'eth' or n[:3] == 'gre':
                        r += [{"interface": n, "status": int(s) == 1}]
                return r
            except self.snmp.TimeOutError:
                raise self.NotSupportedError()
