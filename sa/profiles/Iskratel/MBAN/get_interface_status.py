# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Iskratel.MBAN.get_interface_status
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
    name = "Iskratel.MBAN.get_interface_status"
    interface = IGetInterfaceStatus

    rx_port = re.compile(
        r"^(?P<port>\S+?\d+)(\:\d+\_\d+)?\s+(?P<admin_status>Yes|No)\s+"
        r"(?P<oper_status>Yes|No)\s+", re.MULTILINE)

    def execute(self, interface=None):
        r = []
        cmd = "show interface"
        if interface is not None:
            cmd += " interface %s" % interface
        for match in self.rx_port.finditer(self.cli(cmd)):
            r += [{
                "interface": match.group('port'),
                "status": match.group('oper_status') != "No"
            }]
        return r
