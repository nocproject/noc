# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.7200.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus


class Script(BaseScript):
    name = "Alstec.7200.get_interface_status"
    interface = IGetInterfaceStatus

    rx_port = re.compile(
        r"^(?P<port>\d+/\d+).+(?P<oper_status>Up|Down)\s+", re.MULTILINE)

    def execute(self, interface=None):
        r = []
        cmd = "show port"
        if interface is not None:
            cmd += " %s" % interface
        else:
            cmd += " all"
        for match in self.rx_port.finditer(self.cli(cmd)):
            r += [{
                "interface": match.group('port'),
                "status": match.group('oper_status') != "Down"
            }]
        return r
