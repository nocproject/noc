# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Qtech.QSW.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetInterfaceStatus


class Script(noc.sa.script.Script):
    name = "Qtech.QSW.get_interface_status"
    implements = [IGetInterfaceStatus]

    rx_interface_status = re.compile(
        r"^(?P<interface>\S+)\s+(\S+|)\s+(?P<status>(up|down))\s",
        re.MULTILINE)

    def execute(self, interface=None):
        r = []
        # Try SNMP first
        if self.snmp and self.access_profile.snmp_ro:
            try:
                for n, s in self.snmp.join_tables("1.3.6.1.2.1.31.1.1.1.1",
                    "1.3.6.1.2.1.2.2.1.8", bulk=True):  # IF-MIB
                    if n[:1] == 'e' or n[:1] == 'g' or n[:1] == 't':
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
        if interface:
            cmd = "show interface brief ethernet %s" % interface[1:]
        else:
            cmd = "show interface brief"
        for match in self.rx_interface_status.finditer(self.cli(cmd)):
            iface = match.group("interface")
            if iface[:1] == 'e' or iface[:1] == 'g' or iface[:1] == 't':
                r.append({
                        "interface": iface,
                        "status": match.group("status") == "up"
                        })
        return r
