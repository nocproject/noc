# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus
from noc.lib.mib import mib


class Script(BaseScript):
    name = "Zyxel.ZyNOS.get_interface_status"
    interface = IGetInterfaceStatus
    rx_link = re.compile(
        r"Port Info\s+Port NO\.\s+:(?P<interface>\d+)\s*Link"
        r"\s+:(?P<status>(1[02]+[MG]/[FH]\s*(Copper|SFP)?)|Down)",
        re.MULTILINE | re.IGNORECASE
    )

    def execute(self, interface=None):
        if self.has_snmp():
            try:
                r = []
                if interface is None:
                    # Get all interfaces
                    for i, n, s in self.snmp.join(
                        mib["IF-MIB::ifName"],
                        mib["IF-MIB::ifOperStatus"]
                    ):
                        if i > 1023:
                            break
                        if n == "enet0":
                            continue  # Skip outbound management
                        r += [{
                            "interface": n,
                            "status": s == 1
                        }]
                    return r
                else:
                    # Get single interface
                    n = self.snmp.get(mib["IF-MIB::ifName", int(interface)]
                    s = self.snmp.get(mib["IF-MIB::ifOperStatus", int(interface)]
                    return [{"interface":n, "status": s == 1}]
            except self.snmp.TimeOutError:
                pass
        # Fallback to CLI
        if interface is None:
            interface = "*"
        try:
            s = self.cli("show interfaces %s" % interface)
        except self.CLISyntaxError:
            raise self.NotSupportedError()

        r = []
        for match in self.rx_link.finditer(s):
            r += [{
            "interface": match.group("interface"),
            "status": match.group("status").lower() != "down"
         }]
        return r
