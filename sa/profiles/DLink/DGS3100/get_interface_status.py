# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# DLink.DGS3100.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus
import re


class Script(BaseScript):
    name = "DLink.DGS3100.get_interface_status"
    interface = IGetInterfaceStatus
=======
##----------------------------------------------------------------------
## DLink.DGS3100.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaceStatus
import re


class Script(NOCScript):
    name = "DLink.DGS3100.get_interface_status"
    implements = [IGetInterfaceStatus]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_line = re.compile(
        r"^\s*(?P<interface>\S+)\s+(Enabled|Disabled)\s+\S+\s+"
        r"(?P<status>.+)\s+(Enabled|Disabled)\s*$",
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
<<<<<<< HEAD
                for i, n, s in self.snmp.join([
                    "1.3.6.1.2.1.31.1.1.1.1",
                    "1.3.6.1.2.1.2.2.1.8"
                ]):
=======
                for n, s in self.snmp.join_tables(
                        "1.3.6.1.2.1.31.1.1.1.1",
                        "1.3.6.1.2.1.2.2.1.8", bulk=True):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                    if not n.startswith("802.1Q Encapsulation Tag"):
                        if interface is not None and interface == n:
                            r += [{"interface": n, "status": int(s) == 1}]
                        else:
                            r += [{"interface": n, "status": int(s) == 1}]
                return r
            except self.snmp.TimeOutError:
                pass
        # Fallback to CLI
        if interface is None:
            interface = "all"
        try:
            s = self.cli("show ports %s" % interface)
        except self.CLISyntaxError:
            raise self.NotSupportedError()

        r = []
        for match in self.rx_line.finditer(s):
            r += [{
                "interface": match.group("interface"),
                "status": match.group("status").strip() != "Link Down"
            }]
        return r
