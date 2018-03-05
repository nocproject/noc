# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Cisco.SMB.get_interface_status
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus


class Script(BaseScript):
    name = "Cisco.SMB.get_interface_status"
    interface = IGetInterfaceStatus

    rx_interface_status = re.compile(
        r"^(?P<interface>\S+).+\s+(?P<status>up|down)\s+.*$", re.IGNORECASE)
    rx_digit = re.compile(r"^[0-9]+$")

    def execute(self, interface=None):
        if self.has_snmp():
            try:
                # Get interface status
                r = []
                # IF-MIB::ifName, IF-MIB::ifOperStatus
                for i, n, s in self.snmp.join([
                    "1.3.6.1.2.1.31.1.1.1.1",
                    "1.3.6.1.2.1.2.2.1.8"
                ]):
                    if (
                        n.startswith("stack-port") or
                        n.startswith("Logical-int")
                    ):
                        continue
                    # ifOperStatus up(1)
                    if self.rx_digit.match(n):
                        n = "Vlan" + n
                    r += [{"interface": n, "status": int(s) == 1}]
                return r
            except self.snmp.TimeOutError:
                pass
        # Fallback to CLI
        r = []
        if interface:
            cmd = "show interfaces status %s" % interface
        else:
            cmd = "show interfaces status"

        for ll in self.cli(cmd).splitlines():
            match = self.rx_interface_status.match(ll)
            if match:
                r += [{
                    "interface": match.group("interface"),
                    "status": match.group("status").lower() == "up"
                }]
        return r
