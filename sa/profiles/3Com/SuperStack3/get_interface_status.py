# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# 3Com.SuperStack3.get_interface_status
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus


class Script(BaseScript):
    name = "3Com.SuperStack3.get_interface_status"
    interface = IGetInterfaceStatus

    rx_line = re.compile(
        r"^(?P<interface>\d+\:\d+)\s+(?P<status>Active|Inactive)",
        re.MULTILINE)

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
            cmd = "bridge port summary %s" % interface
        else:
            cmd = "bridge port summary all"
        for match in self.rx_line.finditer(self.cli(cmd)):
            r += [{
                "interface": match.group("interface"),
                "status": match.group("status") == "Active"
            }]
        return r
