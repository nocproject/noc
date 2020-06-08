# ---------------------------------------------------------------------
# Iskratel.MSAN.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.snmp.render import render_mac


class Script(BaseScript):
    name = "Iskratel.MSAN.get_chassis_id"
    interface = IGetChassisID
    cache = True

    def execute_snmp(self, **kwargs):
        mac = self.snmp.get(
            "1.3.6.1.4.1.1332.1.1.5.2.1.2.3.4.0",
            display_hints={"1.3.6.1.4.1.1332.1.1.5.2.1.2.3.4.0": render_mac},
        )
        if mac:
            return {"first_chassis_mac": mac, "last_chassis_mac": mac}
        raise NotImplementedError

    rx_mac = re.compile(r"Burned In MAC Address\.+ (?P<mac>\S+)\n")

    def execute_cli(self, **kwargs):
        v = self.cli("show hardware", cached=True)
        match = self.rx_mac.search(v)
        if match:
            return {"first_chassis_mac": match.group("mac"), "last_chassis_mac": match.group("mac")}
        raise NotImplementedError
