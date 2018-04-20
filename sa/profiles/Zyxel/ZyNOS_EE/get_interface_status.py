# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Zyxel.ZyNOS_EE.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus


class Script(BaseScript):
    name = "Zyxel.ZyNOS_EE.get_interface_status"
    interface = IGetInterfaceStatus
=======
##----------------------------------------------------------------------
## Zyxel.ZyNOS_EE.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaceStatus


class Script(NOCScript):
    name = "Zyxel.ZyNOS_EE.get_interface_status"
    implements = [IGetInterfaceStatus]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_link = re.compile(
        r"^( |)(?P<interface>\d+)\s+\d+\s+(?P<status>\d)\s+\S+\s+\S+\s+\S+$",
        re.MULTILINE)

    def execute(self, interface=None):
        r = []

        # Try SNMP first
<<<<<<< HEAD
        if self.has_snmp():
=======
        if self.snmp and self.access_profile.snmp_ro:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            try:
                if interface is None:
                    # Join # IF-MIB::ifIndex, IF-MIB::ifOperStatus
                    for n, s in self.snmp.join_tables("1.3.6.1.2.1.2.2.1.1",
                                                      "1.3.6.1.2.1.2.2.1.8",
<<<<<<< HEAD
=======
                                                      bulk=True,
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                                                      max_index=1023):
                        r.append({
                            "interface": n,
                            "status": int(s) == 1  # ifOperStatus up(1)
                            })
                    return r
                else:
                    n = self.snmp.get("1.3.6.1.2.1.2.2.1.1.%d"
                                    % int(interface))
                    s = self.snmp.get("1.3.6.1.2.1.2.2.1.8.%d"
                                    % int(interface))
                    return [{"interface":n, "status":int(s) == 1}]
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        try:
            s = self.cli("sys sw portstatus")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        for match in self.rx_link.finditer(s):
            if interface is None:
                r.append({
                        "interface": match.group("interface"),
                        "status": match.group("status") == '1'
                        })
            else:
                iface = match.group("interface")
                if interface == iface:
                    r = [{
                        "interface": iface,
                        "status": match.group("status") == '1'
                        }]
        if not r:
            raise self.NotSupportedError()
        return r
