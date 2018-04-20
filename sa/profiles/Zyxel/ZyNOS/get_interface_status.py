# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Zyxel.ZyNOS.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
=======
##----------------------------------------------------------------------
## Zyxel.ZyNOS.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

# Python modules
import re
# NOC modules
<<<<<<< HEAD
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus
from noc.core.mib import mib


class Script(BaseScript):
    name = "Zyxel.ZyNOS.get_interface_status"
    interface = IGetInterfaceStatus
    rx_link = re.compile(
        r"Port Info\s+Port NO\.\s+:(?P<interface>\d+)\s*Link"
        r"\s+:(?P<status>(1[02]+[MG]/[FH]\s*(Copper|SFP)?)|Down)",
        re.MULTILINE | re.IGNORECASE
    )
    cache = True

    def execute(self, interface=None):
        if self.has_snmp():
            try:
                r = []
                if interface is None:
                    # Get all interfaces
                    for i, n, s in self.snmp.join([
                        mib["IF-MIB::ifName"],
                        mib["IF-MIB::ifOperStatus"]
                    ]):
                        if i > 1023:
                            break
                        if n == "enet0":
                            continue  # Skip outbound management
                        r += [{
                            "interface": n,
                            "status": s == 1
                        }]
                    if r:
                        return r
                else:
                    # Get single interface
                    n = self.snmp.get(mib["IF-MIB::ifName", int(interface)])
                    s = self.snmp.get(mib["IF-MIB::ifOperStatus", int(interface)])
                    return [{"interface": n, "status": s == 1}]
            except self.snmp.TimeOutError:
                pass
        self.logger.info("Nothing get on SNMP, go to CLI")
=======
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaceStatus


class Script(NOCScript):
    name = "Zyxel.ZyNOS.get_interface_status"
    implements = [IGetInterfaceStatus]
    rx_link = re.compile(r"Port Info\s+Port NO\.\s+:(?P<interface>\d+)\s*Link"
                    r"\s+:(?P<status>(1[02]+[MG]/[FH]\s*(Copper|SFP)?)|Down)",
                    re.MULTILINE | re.IGNORECASE)

    def execute(self, interface=None):
        if self.snmp and self.access_profile.snmp_ro:
            try:
                r = []
                if interface is None:
                    # Join # IF-MIB::ifName, IF-MIB::ifOperStatus
                    # use max_index to skip vlans
                    for n, s in self.snmp.join_tables("1.3.6.1.2.1.31.1.1.1.1",
                                                      "1.3.6.1.2.1.2.2.1.8",
                                                      bulk=True,
                                                      max_index=1023):
#                        if n == "enet0":  # tmp - skip Outbound management
#                            continue
                        # ifOperStatus up(1)
                        r += [{"interface": n, "status": int(s) == 1}]
                    return r
                else:
                    n = self.snmp.get("1.3.6.1.2.1.31.1.1.1.1.%d"
                                    % int(interface))
                    s = self.snmp.get("1.3.6.1.2.1.2.2.1.8.%d"
                                    % int(interface))
                    return [{"interface":n, "status":int(s) == 1}]
            except self.snmp.TimeOutError:
                pass
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        # Fallback to CLI
        if interface is None:
            interface = "*"
        try:
            s = self.cli("show interfaces %s" % interface)
        except self.CLISyntaxError:
            raise self.NotSupportedError()

        r = []
        for match in self.rx_link.finditer(s):
            r += [{
<<<<<<< HEAD
                "interface": match.group("interface"),
                "status": match.group("status").lower() != "down"
            }]
=======
            "interface": match.group("interface"),
            "status": match.group("status").lower() != "down"
         }]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        return r
