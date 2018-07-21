# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DVG.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "DLink.DVG.get_chassis_id"
    interface = IGetChassisID

    rx_mac = re.compile(r"^WAN MAC \[+(?P<mac>\S+)+\]$", re.MULTILINE)
    OIDS_CHECK = ["1.3.6.1.2.1.2.2.1.6.2"]

    def execute_cli(self):
        # Try SNMP first
        if self.has_snmp():
            try:
                return self.execute_snmp()
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        match = self.re_search(self.rx_mac,
                               self.cli("GET STATUS WAN", cached=True))
        if not match:
            raise self.NotSupportedError()
        mac = match.group("mac")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
