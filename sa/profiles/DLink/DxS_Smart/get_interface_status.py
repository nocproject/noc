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
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaceStatus


class Script(NOCScript):
    name = "DLink.DxS_Smart.get_interface_status"
    implements = [IGetInterfaceStatus]

    def execute(self, interface=None):
        r = []
        # Try snmp first
        if self.snmp and self.access_profile.snmp_ro:
            try:
                for n, s in self.snmp.join_tables(
                        "1.3.6.1.2.1.31.1.1.1.1",
                        "1.3.6.1.2.1.2.2.1.8", bulk=True):  # IF-MIB
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
