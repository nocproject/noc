# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Juniper.JUNOS.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus


class Script(BaseScript):
    name = "Juniper.JUNOS.get_interface_status"
    interface = IGetInterfaceStatus
=======
##----------------------------------------------------------------------
## Juniper.JUNOS.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus


class Script(NOCScript):
    name = "Juniper.JUNOS.get_interface_status"
    implements = [IGetInterfaceStatus]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_interface_status = re.compile(
        r"^(?P<interface>\S+)\s+(?P<admin>up|down)\s+(?P<oper>up|down)",
        re.IGNORECASE
    )

    def execute(self, interface=None):
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
                    if (
                        interface and
                        interface == self.profile.convert_interface_name(n)
                    ):
                        return [{"interface": n, "status": int(s) == 1}]
                    if not self.profile.valid_interface_name(self, n):
                        continue
                    r += [{"interface": n, "status": int(s) == 1}]
                # XXX: Sometime snmpwalk return only loX interfaces
                if len(r) > 10:
                    return r
=======
                for n, s in self.snmp.join_tables("1.3.6.1.2.1.31.1.1.1.1",
                    "1.3.6.1.2.1.2.2.1.8", bulk=True):
                    if interface \
                    and interface == self.profile.convert_interface_name(n):
                        return [{"interface": n, "status": int(s) == 1}]
                    r += [{"interface": n, "status": int(s) == 1}]
                return r
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            except self.snmp.TimeOutError:
                pass
        # Fallback to CLI
        r = []
        if interface:
            cmd = "show interfaces terse | match \"^%s\" " % interface
        else:
<<<<<<< HEAD
            cmd = "show interfaces terse | except demux"
=======
            cmd = "show interfaces terse"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

        for l in self.cli(cmd).splitlines():
            match = self.rx_interface_status.search(l)
            if match:
                iface = match.group("interface")
<<<<<<< HEAD
                if not self.profile.valid_interface_name(self, iface):
                    continue
=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                if not interface or iface == interface:
                    r += [{
                        "interface": iface,
                        "status": match.group("oper") == "up"
                    }]
        return r
