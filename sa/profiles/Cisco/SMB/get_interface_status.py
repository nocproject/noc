# -*- coding: utf-8 -*-
<<<<<<< HEAD
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
=======
##----------------------------------------------------------------------
## Cisco.SMB.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaceStatus

rx_interface_status = re.compile(r"^(?P<interface>.+?)\s+is\s+\S+,\s+line\s+protocol\s+is\s+(?P<status>up|down).*$", re.IGNORECASE)
rx_interface_status = re.compile(r"^(?P<interface>\S+).+\s+(?P<status>up|down)\s+.*$", re.IGNORECASE)


class Script(NOCScript):
    name = "Cisco.SMB.get_interface_status"
    implements = [IGetInterfaceStatus]

    def execute(self, interface=None):
        if self.snmp and self.access_profile.snmp_ro:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            try:
                # Get interface status
                r = []
                # IF-MIB::ifName, IF-MIB::ifOperStatus
<<<<<<< HEAD
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
=======
                for n, s in self.snmp.join_tables("1.3.6.1.2.1.31.1.1.1.1",
                    "1.3.6.1.2.1.2.2.1.8", bulk=True):
                    # ifOperStatus up(1)
                    if re.match("^[0-9]+$",n):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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

<<<<<<< HEAD
        for ll in self.cli(cmd).splitlines():
            match = self.rx_interface_status.match(ll)
=======
        for l in self.cli(cmd).splitlines():
            match = rx_interface_status.match(l)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            if match:
                r += [{
                    "interface": match.group("interface"),
                    "status": match.group("status").lower() == "up"
                }]
        return r
