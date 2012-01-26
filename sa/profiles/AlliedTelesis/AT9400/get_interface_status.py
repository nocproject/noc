# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlliedTelesis.AT9400.get_interface_status
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
    name = "AlliedTelesis.AT9400.get_interface_status"
    implements = [IGetInterfaceStatus]
    rx_line = re.compile(r"ifIndex\.+ ", re.IGNORECASE | re.MULTILINE)
    rx_if = re.compile(r"(?P<interface>\d+)", re.IGNORECASE | re.MULTILINE)
    rx_oper = re.compile(r"ifOperStatus\.+ (?P<status>Up|Down)", re.IGNORECASE | re.MULTILINE)

    def execute(self, interface=None):
        # Not tested. Must be identical in different vendors
        if self.snmp and self.access_profile.snmp_ro:
            try:
                # Get interface status
                r = []
                # IF-MIB::ifName, IF-MIB::ifOperStatus
                for n, s in self.snmp.join_tables("1.3.6.1.2.1.31.1.1.1.1", "1.3.6.1.2.1.2.2.1.8", bulk=True):
                    if not n.startswith("802.1Q Encapsulation Tag") \
                    and (interface is not None and interface == n):
                        # ifOperStatus up(1)
                        r += [{"interface":n, "status":int(s) == 1}]
                return r
            except self.snmp.TimeOutError:
                pass
        # Fallback to CLI
        if interface is None:
            interface = "ALL"
        try:
            v = self.cli("show interface %s" % interface)
        except self.CLISyntaxError:
            raise self.NotSupportedError()

        r = []
        for s in self.rx_line.split(v)[1:]:
            match = self.rx_if.search(s)
            if not match:
                continue
            iface = match.group("interface")
            match = self.rx_oper.search(s)
            if not match:
                continue
            status = match.group("status")
            r += [{
                "interface": iface,
                "status": status.lower() == "up"
                }]
        return r
