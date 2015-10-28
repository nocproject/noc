# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus

rx_interface_status = re.compile(
    r"^(?P<interface>.+?)\s+is\s+\S+,\s+line\s+protocol\s+is\s+"
    r"(?P<status>up|down).*$", re.IGNORECASE)


class Script(BaseScript):
    name = "Cisco.IOS.get_interface_status"
    interface = IGetInterfaceStatus

    def execute(self, interface=None):
        if self.has_snmp():
            try:
                # Get interface status
                r = []
                # IF-MIB::ifName, IF-MIB::ifOperStatus
                for n, s in self.snmp.join_tables("1.3.6.1.2.1.31.1.1.1.1",
                    "1.3.6.1.2.1.2.2.1.8", bulk=True):
                    # ifOperStatus up(1)
                    if n.startswith("Stack") or n.startswith("Voice") \
                    or n.startswith("SPAN") or n.startswith("VLAN-"):
                        continue
                    if interface \
                    and interface == self.profile.convert_interface_name(n):
                        return [{"interface": n, "status": int(s) == 1}]
                    r += [{"interface": n, "status": int(s) == 1}]
                return r
            except self.snmp.TimeOutError:
                pass
        # Fallback to CLI
        r = []
        if interface:
            cmd = "show interface %s | include line protocol is" % interface
        else:
            cmd = "show interface | include line protocol is"

        for l in self.cli(cmd).splitlines():
            match = rx_interface_status.match(l)
            if match:
                r += [{
                    "interface": match.group("interface"),
                    "status": match.group("status") == "up"
                }]
        return r
