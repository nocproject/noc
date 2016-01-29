# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.AOS.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus
from noc.lib.mib import mib


class Script(BaseScript):
    name = "Alcatel.AOS.get_interface_status"
    interface = IGetInterfaceStatus
    rx_line = re.compile(
        r"(?P<interface>\S+)\s+\S+\s+(?P<status>up|down)\s+\S+\d*\s+\d*",
        re.IGNORECASE | re.MULTILINE)

    def execute(self, interface=None):
        if self.has_snmp():
            try:
                # Get interface status
                r = []
                # IF-MIB::ifName, IF-MIB::ifOperStatus
                for i, n, s in self.snmp.join([
                    mib["IF-MIB::ifName"],
                    mib["IF-MIB::ifOperStatus"]
                ]):
                    r += [{"interface": n, "status":int(s) == 1}]
                return r
            except self.snmp.TimeOutError:
                pass
        r = []
        for match in self.rx_line.finditer(self.cli("show interfaces port")):
            r += [{
                "interface": match.group("interface"),
                "status": match.group("status").lower() == "up"
            }]
        return r
