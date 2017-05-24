# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.ALS.get_interface_status
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
    name = "Alstec.ALS.get_interface_status"
    interface = IGetInterfaceStatus

    rx_port = re.compile(
        r"^(?P<port>(?:Gi|Te|Po|e|g|ch)\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+"
        r"(?P<oper_status>Up|Down|Not Present)",
        re.MULTILINE | re.IGNORECASE)

    def execute(self, interface=None):
        r = []
        for match in self.rx_port.finditer(self.cli("show interfaces status")):
            if (interface is not None) and (interface == match.group('port')):
                return [{
                    "interface": match.group('port'),
                    "status": match.group('oper_status') == "Up"
                }]
            r += [{
                "interface": match.group('port'),
                "status": match.group('oper_status') == "Up"
            }]
        return r
