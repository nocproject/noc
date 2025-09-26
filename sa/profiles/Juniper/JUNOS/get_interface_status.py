# ---------------------------------------------------------------------
# Juniper.JUNOS.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
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

    rx_interface_status = re.compile(
        r"^Physical interface: (?P<interface>\S+)\s*,\s+.+Physical link is\s+(?P<oper>Up|Down)"
    )

    def execute_snmp(self, interface=None):
        # Get interface status
        r = []
        # IF-MIB::ifName, IF-MIB::ifOperStatus
        for i, n, s in self.snmp.join(["1.3.6.1.2.1.31.1.1.1.1", "1.3.6.1.2.1.2.2.1.8"]):
            if interface and interface == self.profile.convert_interface_name(n):
                return [{"interface": n, "status": int(s) == 1}]
            if not self.profile.valid_interface_name(self, n):
                continue
            r += [{"interface": n, "status": int(s) == 1}]
        # XXX: Sometime snmpwalk return only loX interfaces
        if len(r) > 10:
            return r
        return []

    def execute_cli(self, interface=None):
        r = []
        cmd = "show interfaces media | match interface:"
        for l in self.cli(cmd).splitlines():
            match = self.rx_interface_status.search(l)
            if match:
                iface = match.group("interface")
                if not self.profile.valid_interface_name(self, iface):
                    continue
                if not interface or iface == interface:
                    r += [{"interface": iface, "status": match.group("oper") == "Up"}]
        return r
