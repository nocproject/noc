# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Alcatel.TIMOS.get_interface_status
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus


class Script(BaseScript):
    name = "Alcatel.TIMOS.get_interface_status"
    interface = IGetInterfaceStatus

    rx_port = re.compile(
        r"^(?P<interface>\d+/\d+/\d+|[AB]/\d+)\s+(?P<adm_status>Up|Down)\s+"
        r"(?P<oper_status>Yes|No)", re.MULTILINE)
    rx_lag = re.compile(
        r"^(?P<number>\d+)\s+(?:up|down)\s+(?P<oper_status>up|down)\s+",
        re.MULTILINE)

    def execute(self, interface=None):
        r = []
        cmd = "show port"
        if interface:
            cmd += " %s" % interface
        for match in self.rx_port.finditer(self.cli(cmd)):
            r += [{
                "interface": match.group("interface"),
                "status": match.group("oper_status") == "Yes"
            }]
        for match in self.rx_lag.finditer(self.cli("show lag")):
            r += [{
                "interface": "lag-" + match.group("number"),
                "status": match.group("oper_status") == "up"
            }]
        return r
