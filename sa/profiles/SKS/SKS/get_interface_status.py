# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# SKS.SKS.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus


class Script(BaseScript):
    name = "SKS.SKS.get_interface_status"
    interface = IGetInterfaceStatus

    rx_port1 = re.compile(
        r"^(?P<port>(?:Gi|Te|Po)\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+"
        r"(?P<oper_status>Up|Down|Not Present)",
        re.MULTILINE | re.IGNORECASE)
    rx_port2 = re.compile(
        r"^(?P<port>[fgt]\d\S*).*?(?P<oper_status>up|down).*\n",
        re.MULTILINE)

    def execute(self, interface=None):
        r = []
        try:
            c = self.cli("show interfaces status")
            rx_port = self.rx_port1
        except self.CLISyntaxError:
            c = self.cli("show interface brief")
            rx_port = self.rx_port2
        for match in rx_port.finditer(c):
            if (interface is not None) and (interface == match.group('port')):
                return [{
                    "interface": match.group('port'),
                    "status": match.group('oper_status').lower() == "up"
                }]
            r += [{
                "interface": match.group('port'),
                "status": match.group('oper_status').lower() == "up"
            }]
        return r
