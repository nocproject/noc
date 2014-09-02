# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaceStatus


class Script(NOCScript):
    name = "DLink.DxS.get_interface_status"
    implements = [IGetInterfaceStatus]

    def execute(self, interface=None):
        r = []
        # Try SNMP first
        if self.snmp and self.access_profile.snmp_ro:
            try:
                # Get interface status IF-MIB
                for n, s in self.snmp.join_tables("1.3.6.1.2.1.31.1.1.1.1",
                                                  "1.3.6.1.2.1.2.2.1.8",
                                                   bulk=True):
                    if '/' in n:
                        iface = n.split('/')[1]
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

        # Fallback to CLI
        ports = self.profile.get_ports(self, interface)
        for p in ports:
            if interface is not None:
                if interface == p['port']:
                    return [{
                        "interface": interface,
                        "status": p['status']
                    }]
                    break
            else:
                r += [{
                    "interface": p['port'],
                    "status": p['status']
                }]
        return r
