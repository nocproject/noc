# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Planet.WGSD.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus
from noc.core.mib import mib


class Script(BaseScript):
    name = "Planet.WGSD.get_interface_status"
    interface = IGetInterfaceStatus

    rx_interface_status = re.compile(
        r"^(?P<interface>\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(?P<status>Up|Down)\s+\S+\s+\S.*$",
        re.MULTILINE,
    )

    def execute_snmp(self, interface=None):
        r = []
        for n, s in self.snmp.join_tables(mib["IF-MIB::ifName"], mib["IF-MIB::ifOperStatus"]):
            if n[:2] == "fa" or n[:2] == "gi" or n[:2] == "te":
                if interface:
                    if n == interface:
                        r.append({"interface": n, "status": int(s) == 1})
                else:
                    r.append({"interface": n, "status": int(s) == 1})
        return r

    def execute_cli(self, interface=None):
        r = []
        if interface:
            cmd = "show interfaces status %s" % interface
        else:
            cmd = "show interfaces status"
        for match in self.rx_interface_status.finditer(self.cli(cmd)):
            iface = match.group("interface")
            if iface[:2] == "fa" or iface[:2] == "gi" or iface[:2] == "te":
                r.append(
                    {"interface": match.group("interface"), "status": match.group("status") == "Up"}
                )
        return r
