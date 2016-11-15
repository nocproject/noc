# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DES21xx.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus


class Script(BaseScript):
    name = "DLink.DES21xx.get_interface_status"
    cache = True
    interface = IGetInterfaceStatus
    rx_link = re.compile(r"^(?P<interface>\d+)\s+([01M HFaulf]+|Auto)\s+" \
                          "\S+\s+\S+\s+(?P<status>([01M HFaulf]+|Down))$",
                          re.MULTILINE | re.IGNORECASE)

    def execute(self, interface=None):
        """
        if self.has_snmp():
            try:
                r = []
                if interface is None:
                    # Join # IF-MIB::ifName, IF-MIB::ifOperStatus
                    for n, s in self.snmp.join_tables("1.3.6.1.2.1.31.1.1.1.1",
                                                      "1.3.6.1.2.1.2.2.1.8",
                                                      max_index=1023):
                        r += [{"interface": n, "status": int(s) == 1}]  # ifOperStatus up(1)
                    return r
                else:
                    n = self.snmp.get("1.3.6.1.2.1.31.1.1.1.1.%d" % int(interface))
                    s = self.snmp.get("1.3.6.1.2.1.2.2.1.8.%d" % int(interface))
                    return [{"interface": n, "status": int(s) == 1}]
            except self.snmp.TimeOutError:
                pass
        # Fallback to CLI
        """
        if interface is None:
            interface = ""
        try:
            s = self.cli("show ports %s" % interface, cached=True)
        except self.CLISyntaxError:
            raise self.NotSupportedError()

        r = []
        for match in self.rx_link.finditer(s):
            r += [{
            "interface": match.group("interface").lstrip('0'),
               "status": match.group("status").lower() != "down"
         }]
        return r
