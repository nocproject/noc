# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Planar.SDO3000.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Planar.SDO3000.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_mac = re.compile(r"^\s+MAC Address:\s+(?P<mac>\S+)$", re.MULTILINE)

    def execute_snmp(self, **kwargs):
        try:
            # PLANAR-sdo3002-MIB::macAddress
            mac = self.snmp.get("1.3.6.1.4.1.32108.1.7.1.4.0")
            return [{"first_chassis_mac": mac, "last_chassis_mac": mac}]
        except self.snmp.TimeOutError:
            raise self.NotSupportedError

    def execute_cli(self, **kwargs):
        cmd = self.cli("1")  # Enter Identification menu
        match = self.rx_mac.search(cmd)
        if match:
            mac = match.group("mac")
        else:
            raise self.NotSupportedError
        return [{"first_chassis_mac": mac, "last_chassis_mac": mac}]
