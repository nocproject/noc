# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DVG.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus


class Script(BaseScript):
    name = "DLink.DVG.get_interface_status"
    interface = IGetInterfaceStatus

    def execute(self, interface=None):
        r = []
        # Only one way: SNMP.
        if self.has_snmp():
            try:
                for n, s in self.snmp.join_tables("1.3.6.1.2.1.2.2.1.2",
                                                  "1.3.6.1.2.1.2.2.1.8",
                                                  bulk=True):  # IF-MIB
                    if n[:3] == 'eth' or n[:3] == 'gre':
                        r += [{"interface": n, "status": int(s) == 1}]
                return r
            except self.snmp.TimeOutError:
                raise self.NotSupportedError()
