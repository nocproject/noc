# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Qtech.QSW.get_interface_status
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
    name = "Qtech.QSW.get_interface_status"
    interface = IGetInterfaceStatus
=======
##----------------------------------------------------------------------
## Qtech.QSW.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetInterfaceStatus


class Script(noc.sa.script.Script):
    name = "Qtech.QSW.get_interface_status"
    implements = [IGetInterfaceStatus]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_interface_status = re.compile(
        r"^(?P<interface>\S+)\s+(\S+|)\s+(?P<status>(up|down))\s",
        re.MULTILINE)
    rx_interface_status1 = re.compile(
        r"^(?P<interface>\S+)\s+(?P<status>UP|DOWN)", re.MULTILINE)

    def execute(self, interface=None):
        r = []
        # Try SNMP first
<<<<<<< HEAD
        if self.has_snmp():
            try:
                for i, n, s in self.snmp.join([
                    "1.3.6.1.2.1.31.1.1.1.1",
                    "1.3.6.1.2.1.2.2.1.8"
                ]):  # IF-MIB
=======
        if self.snmp and self.access_profile.snmp_ro:
            try:
                for n, s in self.snmp.join_tables("1.3.6.1.2.1.31.1.1.1.1",
                    "1.3.6.1.2.1.2.2.1.8", bulk=True):  # IF-MIB
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                    if n[:1] == 'e' or n[:1] == 'g' or n[:1] == 't':
                        if interface:
                            if n == interface:
                                r.append({
<<<<<<< HEAD
                                    "interface": n,
                                    "status": int(s) == 1
                                })
                        else:
                            r.append({
                                "interface": n,
                                "status": int(s) == 1
                            })
=======
                                    "interface": self.profile.convert_interface_name(n),
                                    "status": int(s) == 1
                                    })
                        else:
                            r.append({
                                "interface": self.profile.convert_interface_name(n),
                                "status": int(s) == 1
                                })
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                return r
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        if interface:
            cmd = "show interface brief ethernet %s" % interface[1:]
        else:
            cmd = "show interface brief"
        try:
            c = self.cli(cmd)
            for match in self.rx_interface_status.finditer(c):
                iface = match.group("interface")
                if iface[:1] == 'e' or iface[:1] == 'g' or iface[:1] == 't':
                    r.append({
<<<<<<< HEAD
                        "interface": iface,
=======
                        "interface": self.profile.convert_interface_name(iface),
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                        "status": match.group("status") == "up"
                    })
        except self.CLISyntaxError:
            if interface:
                cmd = "show interface ethernet %s status" % interface
            else:
                cmd = "show interface ethernet status"
            c = self.cli(cmd)
            for match in self.rx_interface_status1.finditer(c):
                iface = match.group("interface")
                r.append({
<<<<<<< HEAD
                    "interface": iface,
=======
                    "interface": self.profile.convert_interface_name(iface),
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                    "status": match.group("status") == "UP"
                })

        return r
