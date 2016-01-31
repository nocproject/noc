# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DGS3100.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus
import re


class Script(BaseScript):
    name = "DLink.DGS3100.get_interface_status"
    interface = IGetInterfaceStatus
    rx_line = re.compile(
        r"^\s*(?P<interface>\S+)\s+(Enabled|Disabled)\s+\S+\s+"
        r"(?P<status>.+)\s+(Enabled|Disabled)\s*$",
        re.IGNORECASE | re.MULTILINE)

    def execute(self, interface=None):
        # Not tested. Must be identical in different vendors
        if self.has_snmp():
            try:
                # Get interface status
                r = []
                # IF-MIB::ifName, IF-MIB::ifOperStatus
                for i, n, s in self.snmp.join([
                    "1.3.6.1.2.1.31.1.1.1.1",
                    "1.3.6.1.2.1.2.2.1.8"
                ]):
                    if not n.startswith("802.1Q Encapsulation Tag"):
                        if interface is not None and interface == n:
                            r += [{"interface": n, "status": int(s) == 1}]
                        else:
                            r += [{"interface": n, "status": int(s) == 1}]
                return r
            except self.snmp.TimeOutError:
                pass
        # Fallback to CLI
        if interface is None:
            interface = "all"
        try:
            s = self.cli("show ports %s" % interface)
        except self.CLISyntaxError:
            raise self.NotSupportedError()

        r = []
        for match in self.rx_line.finditer(s):
            r += [{
                "interface": match.group("interface"),
                "status": match.group("status").strip() != "Link Down"
            }]
        return r
