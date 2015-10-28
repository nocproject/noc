# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus


class Script(BaseScript):
    name = "Zyxel.ZyNOS.get_interface_status"
    interface = IGetInterfaceStatus
    rx_link = re.compile(r"Port Info\s+Port NO\.\s+:(?P<interface>\d+)\s*Link"
                    r"\s+:(?P<status>(1[02]+[MG]/[FH]\s*(Copper|SFP)?)|Down)",
                    re.MULTILINE | re.IGNORECASE)

    def execute(self, interface=None):
        if self.has_snmp():
            try:
                r = []
                if interface is None:
                    # Join # IF-MIB::ifName, IF-MIB::ifOperStatus
                    # use max_index to skip vlans
                    for n, s in self.snmp.join_tables("1.3.6.1.2.1.31.1.1.1.1",
                                                      "1.3.6.1.2.1.2.2.1.8",
                                                      bulk=True,
                                                      max_index=1023):
#                        if n == "enet0":  # tmp - skip Outbound management
#                            continue
                        # ifOperStatus up(1)
                        r += [{"interface": n, "status": int(s) == 1}]
                    return r
                else:
                    n = self.snmp.get("1.3.6.1.2.1.31.1.1.1.1.%d"
                                    % int(interface))
                    s = self.snmp.get("1.3.6.1.2.1.2.2.1.8.%d"
                                    % int(interface))
                    return [{"interface":n, "status":int(s) == 1}]
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
