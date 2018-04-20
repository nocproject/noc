# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ----------------------------------------------------------------------
# Alcatel.AOS.get_interface_status
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus
from noc.core.mib import mib


class Script(BaseScript):
    name = "Alcatel.AOS.get_interface_status"
    interface = IGetInterfaceStatus
=======
##----------------------------------------------------------------------
## Alcatel.AOS.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaceStatus
import re


class Script(NOCScript):
    name = "Alcatel.AOS.get_interface_status"
    implements = [IGetInterfaceStatus]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_line = re.compile(
        r"(?P<interface>\S+)\s+\S+\s+(?P<status>up|down)\s+\S+\d*\s+\d*",
        re.IGNORECASE | re.MULTILINE)

    def execute(self, interface=None):
<<<<<<< HEAD
        if self.has_snmp():
=======
        # Not tested. Must be identical in different vendors
        if self.snmp and self.access_profile.snmp_ro:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            try:
                # Get interface status
                r = []
                # IF-MIB::ifName, IF-MIB::ifOperStatus
<<<<<<< HEAD
                for i, n, s in self.snmp.join([
                    mib["IF-MIB::ifName"],
                    mib["IF-MIB::ifOperStatus"]
                ]):
                    r += [{"interface": n, "status":int(s) == 1}]
=======
                for n, s in self.snmp.join_tables("1.3.6.1.2.1.31.1.1.1.1",
                                                  "1.3.6.1.2.1.2.2.1.8",
                                                  bulk=True):
                    r += [{"interface":n, "status":int(s) == 1}]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                return r
            except self.snmp.TimeOutError:
                pass
        r = []
        for match in self.rx_line.finditer(self.cli("show interfaces port")):
            r += [{
                "interface": match.group("interface"),
                "status": match.group("status").lower() == "up"
<<<<<<< HEAD
            }]
=======
                }]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        return r
