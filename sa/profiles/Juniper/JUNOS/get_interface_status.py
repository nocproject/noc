# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOS.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus


class Script(NOCScript):
    name = "Juniper.JUNOS.get_interface_status"
    implements = [IGetInterfaceStatus]

    rx_interface_status = re.compile(
        r"^(?P<interface>\S+)\s+(?P<admin>up|down)\s+(?P<oper>up|down)",
        re.IGNORECASE
    )

    def execute(self, interface=None):
        if self.has_snmp():
            try:
                # Get interface status
                r = []
                # IF-MIB::ifName, IF-MIB::ifOperStatus
                for n, s in self.snmp.join_tables("1.3.6.1.2.1.31.1.1.1.1",
                    "1.3.6.1.2.1.2.2.1.8", bulk=True):
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
            cmd = "show interfaces terse | match \"^%s\" " % interface
        else:
            cmd = "show interfaces terse"

        for l in self.cli(cmd).splitlines():
            match = self.rx_interface_status.search(l)
            if match:
                iface = match.group("interface")
                if not interface or iface == interface:
                    r += [{
                        "interface": iface,
                        "status": match.group("oper") == "up"
                    }]
        return r
