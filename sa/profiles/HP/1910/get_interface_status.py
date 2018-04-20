# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# HP.1910.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus


class Script(BaseScript):
    name = "HP.1910.get_interface_status"
    interface = IGetInterfaceStatus
=======
##----------------------------------------------------------------------
## HP.1910.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetInterfaceStatus


class Script(noc.sa.script.Script):
    name = "HP.1910.get_interface_status"
    implements = [IGetInterfaceStatus]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_interface_status = re.compile(
        r"^(?P<interface>\S+)\s+(?P<status>UP|DOWN)\s+\S+\s+\S+\s+\S+\s+\d+\s*$",
        re.MULTILINE)

    def execute(self, interface=None):
        r = []
        # Try SNMP first
<<<<<<< HEAD
        if self.has_snmp():
            try:
                for n, s in self.snmp.join_tables("1.3.6.1.2.1.31.1.1.1.1",
                    "1.3.6.1.2.1.2.2.1.8"):  # IF-MIB
=======
        if self.snmp and self.access_profile.snmp_ro:
            try:
                for n, s in self.snmp.join_tables("1.3.6.1.2.1.31.1.1.1.1",
                    "1.3.6.1.2.1.2.2.1.8", bulk=True):  # IF-MIB
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                    if 'Ethernet' in n:
                        if interface:
                            if n == interface.replace('Gi ', 'GigabitEthernet'):
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
            cmd = "display interface brief %s" % interface
        else:
            cmd = "display interface brief"
        for match in self.rx_interface_status.finditer(self.cli(cmd)):
            r.append({
                "interface": match.group("interface"),
                "status": match.group("status") == "UP"
                })
        if not r:
            if interface:
                cmd = "display brief interface %s" % interface
            else:
                cmd = "display brief interface"
            for match in self.rx_interface_status.finditer(self.cli(cmd)):
                r.append({
                    "interface": match.group("interface"),
                    "status": match.group("status") == "UP"
                    })
        return r
