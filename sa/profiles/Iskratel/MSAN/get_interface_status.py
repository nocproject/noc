# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Iskratel.MSAN.get_interface_status
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
    name = "Iskratel.MSAN.get_interface_status"
    interface = IGetInterfaceStatus

    rx_port = re.compile(
        r"^(?P<port>\d+/\d+)\s+(?:\s+|PC|PC Mbr)\s+"
        r"(?P<admin_status>Enable|Disable)\s+"
        r"(?:Auto|1000 Full)\s+"
        r"(?:Auto|1000 Full)\s+"
        r"(?P<oper_status>Up|Down)\s+(?:Enable|Disable)\s+"
        r"(?:Enable|Disable)(?P<descr>.*?)?\n", re.MULTILINE)

    def execute(self, interface=None):
        r = []
        for match in self.rx_port.finditer(self.cli("show port all")):
            if (interface is not None) and (interface == match.group('port')):
                return [{
                    "interface": match.group('port'),
                    "status": match.group('oper_status') != "Down"
                }]
            r += [{
                "interface": match.group('port'),
                "status": match.group('oper_status') != "Down"
            }]
        return r
