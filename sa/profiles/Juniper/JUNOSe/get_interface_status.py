# ---------------------------------------------------------------------
# Juniper.JUNOSe.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus


class Script(BaseScript):
    name = "Juniper.JUNOSe.get_interface_status"
    interface = IGetInterfaceStatus

    rx_interface_status = re.compile(r"(?P<interface>\S+)\s+is\s+(?P<status>Up|Down)")

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
        v = self.profile.get_interfaces_list(self)
        if interface:
            cmd = "show interface %s | include Administrative status" % interface
            s = self.cli(cmd)
            match = self.rx_interface_status.search(s)
            if match:
                return [
                    {"interface": match.group("interface"), "status": match.group("status") == "Up"}
                ]
        else:
            for interface in v:
                cmd = "show interface %s | include Administrative status" % interface
                s = self.cli(cmd)
                match = self.rx_interface_status.search(s)
                if match:
                    r += [
                        {
                            "interface": match.group("interface"),
                            "status": match.group("status") == "Up",
                        }
                    ]
        return r
