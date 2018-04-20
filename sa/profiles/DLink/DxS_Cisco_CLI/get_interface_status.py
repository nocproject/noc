# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# DLink.DxS_Cisco_CLI.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus
import re


class Script(BaseScript):
    name = "DLink.DxS_Cisco_CLI.get_interface_status"
    interface = IGetInterfaceStatus
=======
##----------------------------------------------------------------------
## DLink.DxS_Cisco_CLI.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaceStatus
import re


class Script(NOCScript):
    name = "DLink.DxS_Cisco_CLI.get_interface_status"
    implements = [IGetInterfaceStatus]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_line = re.compile(
        r"^(?P<interface>\S+\s*\d+(\/\d+)?)\s+(?P<status>up|down)\s+\d+\s+"
        r"(Unknown|Half|Full)\s+\S+\s+(copper|fiber)\s*$",
        re.IGNORECASE | re.MULTILINE)

    def execute(self, interface=None):
        # Not tested. Must be identical in different vendors
<<<<<<< HEAD
        if self.has_snmp():
=======
        if self.snmp and self.access_profile.snmp_ro:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            try:
                # Get interface status
                r = []
                # IF-MIB::ifName, IF-MIB::ifOperStatus
                for n, s in self.snmp.join_tables("1.3.6.1.2.1.31.1.1.1.1",
<<<<<<< HEAD
                                                  "1.3.6.1.2.1.2.2.1.8"):
=======
                                                  "1.3.6.1.2.1.2.2.1.8",
                                                  bulk=True):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                    # ifOperStatus up(1)
                    r += [{"interface":n, "status":int(s) == 1}]
                return r
            except self.snmp.TimeOutError:
                pass
        # Fallback to CLI
        r = []
        for match in self.rx_line.finditer(self.cli("show interfaces status")):
            r += [{
                "interface": match.group("interface"),
                "status": match.group("status").lower() == "up"
                }]
        return r
