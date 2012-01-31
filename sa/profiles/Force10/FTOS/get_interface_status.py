# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Force10.FTOS.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetInterfaceStatus
import re

rx_interface_status = re.compile(r"^(?P<interface>\S+\s+\S+)\s+is\s+\S+,\s+line\s+protocol\s+is\s+(?P<status>up|down).*$", re.IGNORECASE)


class Script(noc.sa.script.Script):
    name = "Force10.FTOS.get_interface_status"
    implements = [IGetInterfaceStatus]

    def execute(self, interface=None):
        if self.snmp and self.access_profile.snmp_ro:
            try:
                # Get interface status
                r = []
                # IF-MIB::ifName, IF-MIB::ifOperStatus
                for n, s in self.snmp.join_tables("1.3.6.1.2.1.31.1.1.1.1",
                    "1.3.6.1.2.1.2.2.1.8", bulk=True):
                    # ifOperStatus up(1)
                    r += [{"interface": n, "status": int(s) == 1}]
                return r
            except self.snmp.TimeOutError:
                pass
        # Fallback to CLI
        r = []
        if interface:
            cmd = "show interface %s | grep \"line protocol is\"" % interface
        else:
            cmd = "show interface | grep \"line protocol is\""

        for l in self.cli(cmd).splitlines():
            match = rx_interface_status.match(l)
            if match:
                r += [{
                    "interface": match.group("interface"),
                    "status": match.group("status") == "up"
                }]
        return r
