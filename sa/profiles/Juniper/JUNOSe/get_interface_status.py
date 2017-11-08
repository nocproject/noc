# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Juniper.JUNOSe.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
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

    rx_interface_status = re.compile(
        r"(?P<interface>\S+)\s+is\s+(?P<status>Up|Down)")

    def execute(self, interface=None):
        r = []
        v = self.profile.get_interfaces_list(self)
        if interface:
            cmd = "show interface %s | include Administrative status" % interface
            s = self.cli(cmd)
            match = self.rx_interface_status.search(s)
            if match:
                return [{
                    "interface": match.group("interface"),
                    "status": match.group("status") == "Up"
                }]
        else:
            for interface in v:
                cmd = "show interface %s | include Administrative status" % interface
                s = self.cli(cmd)
                match = self.rx_interface_status.search(s)
                if match:
                    r += [{
                        "interface": match.group("interface"),
                        "status": match.group("status") == "Up"
                    }]
        c = self.cli
        return r
