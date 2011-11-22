# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.MES.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

import noc.sa.script
from noc.sa.interfaces import IGetInterfaceStatus
import re

class Script(noc.sa.script.Script):
    name = "Eltex.MES.get_interface_status"
    implements = [IGetInterfaceStatus]

    rx_interface_status = re.compile(r"^(?P<interface>\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(?P<status>Up|Down)\s+\S+\s+\S.*$", re.MULTILINE)

    def execute(self, interface=None):
        r = []
        # Try snmp first
        if self.snmp and self.access_profile.snmp_ro:
            try:
                for n,s in self.snmp.join_tables("1.3.6.1.2.1.31.1.1.1.1", "1.3.6.1.2.1.2.2.1.8", bulk=True): # IF-MIB
                    if n[:2] == 'gi' or n[:2] == 'te':
                        if interface:
                            if n == interface:
                                r.append({"interface":n, "status":int(s)==1})
                        else:
                            r.append({"interface":n, "status":int(s)==1})
                return r
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        if interface:
            cmd = "show interfaces status %s"%interface
        else:
            cmd = "show interfaces status"
        for match in self.rx_interface_status.finditer(self.cli(cmd)):
            r.append({
                    "interface" : match.group("interface"),
                    "status"    : match.group("status") == "Up"
                    })
        return r
