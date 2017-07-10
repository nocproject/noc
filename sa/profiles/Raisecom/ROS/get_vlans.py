# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Raisecom.ROS.get_vlans
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
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "Raisecom.ROS.get_vlans"
    interface = IGetVlans

    rx_vlan = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+(?P<name>\S+).+\n", re.MULTILINE)

    def execute(self):
        r = []
        for match in self.rx_vlan.finditer(self.cli("show vlan")):
            if match.group('vlan_id') == "1":
                continue
            r.append(match.groupdict())
        return r
