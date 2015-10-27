# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.PON.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import re
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetInterfaceStatus


class Script(noc.sa.script.Script):
    name = "Eltex.PON.get_interface_status"
    implements = [IGetInterfaceStatus]

    rx_uplink = re.compile(
        r"^\s+(?P<interface>\S+ \d+)$",
        re.MULTILINE)

    rx_status = re.compile(
        r"^(?P<interface>\S+ \d+)\s+(?P<status>up|down)\s+\S+\s+\S+\s+\S+"
        r"(\s+\S+|)\s*$", re.MULTILINE)

    def execute(self, interface=None):
        r = []
        """
        # Try SNMP first
        if self.has_snmp():
            try:
                for n, s in self.snmp.join_tables("1.3.6.1.2.1.31.1.1.1.1",
                    "1.3.6.1.2.1.2.2.1.8", bulk=True):  # IF-MIB
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
        """

        # Fallback to CLI
        with self.profile.switch(self):
            if interface:
                cmd = "show interfaces status %s\r" % interface
                match = self.rx_status.search(self.cli(cmd))
                r.append({
                        "interface": interface,
                        "status": match.group("status") == "up"
                        })
            else:
                cmd = "show uplink interfaces\r"
                for match in self.rx_uplink.finditer(self.cli(cmd)):
                    interface = match.group("interface")
                    cmd = "show interfaces status %s\r" % interface
                    match = self.rx_status.search(self.cli(cmd))
                    r.append({
                            "interface": interface,
                            "status": match.group("status") == "up"
                            })
                for port in range(8):
                    interface = "pon-port " + str(port)
                    cmd = "show interfaces status %s\r" % interface
                    match = self.rx_status.search(self.cli(cmd))
                    r.append({
                            "interface": interface,
                            "status": match.group("status") == "up"
                            })
        return r
