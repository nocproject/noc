# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.1910.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus


class Script(BaseScript):
    name = "HP.1910.get_interface_status"
    interface = IGetInterfaceStatus

    rx_interface_status = re.compile(
        r"^(?P<interface>\S+)\s+(?P<status>UP|DOWN)\s+\S+\s+\S+\s+\S+\s+\d+\s*$",
        re.MULTILINE)

    def execute(self, interface=None):
        r = []
        # Try SNMP first
        if self.has_snmp():
            try:
                for n, s in self.snmp.join_tables("1.3.6.1.2.1.31.1.1.1.1",
                    "1.3.6.1.2.1.2.2.1.8", bulk=True):  # IF-MIB
                    if 'Ethernet' in n:
                        if interface:
                            if n == interface.replace('Gi ', 'GigabitEthernet'):
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
        if interface:
            cmd = "display interface brief %s" % interface
        else:
            cmd = "display interface brief"
        for match in self.rx_interface_status.finditer(self.cli(cmd)):
            r.append({
                "interface": match.group("interface"),
                "status": match.group("status") == "UP"
                })
        if not r:
            if interface:
                cmd = "display brief interface %s" % interface
            else:
                cmd = "display brief interface"
            for match in self.rx_interface_status.finditer(self.cli(cmd)):
                r.append({
                    "interface": match.group("interface"),
                    "status": match.group("status") == "UP"
                    })
        return r
