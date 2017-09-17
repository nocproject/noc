# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Rotek.RTBSv1.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus


class Script(BaseScript):
    name = "Rotek.RTBSv1.get_interface_status"
    interface = IGetInterfaceStatus

    def execute(self, interface=None):
        r = []
        # Try SNMP first
        if self.has_snmp():
            try:
                # Get interface status IF-MIB
                for i, n, s in self.snmp.join([
                    "1.3.6.1.2.1.2.2.1.2",
                    "1.3.6.1.2.1.2.2.1.8"
                ]):
                    iface = n
                    if interface is not None:
                        if interface == iface:
                            r = [{
                                    "interface": iface,
                                    "status": int(s) == 1
                                }]
                    else:
                        r.append({
                                    "interface": iface,
                                    "status": int(s) == 1
                                })
                return r
            except self.snmp.TimeOutError:
                pass

