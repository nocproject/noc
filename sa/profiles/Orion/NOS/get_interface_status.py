# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Orion.NOS.get_interface_status
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
    name = "Orion.NOS.get_interface_status"
    interface = IGetInterfaceStatus

    rx_port = re.compile(
        r"^\s*(?P<port>\d+)\s+\S+\s+(?P<oper_status>\S+)",re.MULTILINE)

    def execute(self, interface=None):
        r = []
        for match in self.rx_port.finditer(self.cli("show interface port")):
            if (interface is not None) and (interface == match.group('port')):
                return [{
                    "interface": match.group('port'),
                    "status": match.group('oper_status') != "down"
                }]
            r += [{
                "interface": match.group('port'),
                "status": match.group('oper_status') != "down"
            }]
        return r
