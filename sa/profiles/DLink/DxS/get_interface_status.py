# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaceStatus
import re


class Script(NOCScript):
    name = "DLink.DxS.get_interface_status"
    implements = [IGetInterfaceStatus]
    rx_line = re.compile(r"^\s*(?P<interface>\S+)\s+(?P<type>FE|GE|10GE|Fiber|1000BASE\-T|1000BASE\-X|10GBASE-R)\s+Link (?P<status>Up|Down)\s+(?P<test>\S+)\s+.*$", re.IGNORECASE | re.MULTILINE)

    def execute(self, interface=None):
        r = []
        # Try SNMP first
        if self.snmp and self.access_profile.snmp_ro:
            try:
                # Get interface status IF-MIB
                for n, s in self.snmp.join_tables("1.3.6.1.2.1.31.1.1.1.1",
                                                  "1.3.6.1.2.1.2.2.1.8",
                                                   bulk=True):
                    if '/' in n:
                        iface = n.split('/')[1]
                        if interface is not None:
                            if interface == iface:
                                r = [{
                                        "interface": iface,
                                        "status": int(s) == 1
                                    }]
                        else:
                            r.append({
                                        "interface": iface,
                                        "status": int(s) == 1
                                    })
                return r
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        if interface is None:
            interface = "all"
        try:
            s = self.cli("cable_diag ports %s" % interface)
        except self.CLISyntaxError:
            raise self.NotSupportedError()

        for match in self.rx_line.finditer(s):
            r += [{
                "interface": match.group("interface"),
                "status": match.group("status").lower() == "up"
                }]
        return r
