# ---------------------------------------------------------------------
# Qtech.QSW8200.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.snmp.render import render_mac


class Script(BaseScript):
    name = "Qtech.QSW8200.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac = re.compile(r"System MAC Address: (?P<mac>\S+)")

    def execute_snmp(self, **kwargs):
        mac = self.snmp.get(
            "1.3.6.1.4.1.8886.6.1.1.1.9.0",
            display_hints={"1.3.6.1.4.1.8886.6.1.1.1.9.0": render_mac},
        )
        if mac:
            return {"first_chassis_mac": mac, "last_chassis_mac": mac}

    def execute_cli(self, **kwargs):
        v = self.cli("show version", cached=True)
        match = self.rx_mac.search(v)
        return {"first_chassis_mac": match.group("mac"), "last_chassis_mac": match.group("mac")}
