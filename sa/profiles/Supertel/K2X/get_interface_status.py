# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Supertel.K2X.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus


class Script(BaseScript):
    name = "Supertel.K2X.get_interface_status"
    interface = IGetInterfaceStatus
=======
##----------------------------------------------------------------------
## Supertel.K2X.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaceStatus


class Script(NOCScript):
    name = "Supertel.K2X.get_interface_status"
    implements = [IGetInterfaceStatus]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_interface_status = re.compile(
        r"^(?P<interface>\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+"
        r"(?P<status>(Up|Down|Down\*))\s+\S+\s+\S+\s*$",
        re.MULTILINE)

    def execute(self, interface=None):
        r = []
        # Try SNMP first
<<<<<<< HEAD
        if self.has_snmp():
            try:
                for n, s in self.snmp.join_tables("1.3.6.1.2.1.31.1.1.1.1",
                                                  "1.3.6.1.2.1.2.2.1.8"):
=======
        if self.snmp and self.access_profile.snmp_ro:
            try:
                for n, s in self.snmp.join_tables("1.3.6.1.2.1.31.1.1.1.1",
                                                  "1.3.6.1.2.1.2.2.1.8",
                                                  bulk=True):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                    if n[:1] == 'g':
                        if interface:
                            if n == interface:
                                r.append({
                                    "interface": n,
                                    "status": int(s) == 1
                                    })
                        else:
                            r.append({
                                "interface": n,
                                "status": int(s) == 1
                                })
                return r
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        if interface:
            cmd = "show interfaces status ethernet %s" % interface
        else:
            cmd = "show interfaces status"
        for match in self.rx_interface_status.finditer(self.cli(cmd)):
            iface = match.group("interface")
            r.append({
                "interface": match.group("interface"),
                "status": match.group("status") == "Up"
                })
        return r
