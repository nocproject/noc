# -*- coding: utf-8 -*-
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

    def execute(self, interface=None):
        r = []
        # Only one way: SNMP.
        if self.snmp and self.access_profile.snmp_ro:
            try:
                for n, s in self.snmp.join_tables("1.3.6.1.2.1.2.2.1.2",
                                                  "1.3.6.1.2.1.2.2.1.8",
                                                  bulk=True):  # IF-MIB
                    if n[:3] == 'eth' or n[:3] == 'gre':
                        r += [{"interface": n, "status": int(s) == 1}]
                return r
            except self.snmp.TimeOutError:
                raise self.NotSupportedError()
