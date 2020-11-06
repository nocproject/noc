# ---------------------------------------------------------------------
# Qtech.QSW.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.snmp.render import render_mac


class Script(BaseScript):
    name = "Qtech.QSW.get_chassis_id"
    interface = IGetChassisID
    cache = True
    always_prefer = "S"

    rx_mac = re.compile(r"^(System )?MAC [Aa]ddress\s*:\s+(?P<mac>\S+)$", re.MULTILINE)
    rx_mac1 = re.compile(r"^\d+\s+(?P<mac>\S+)\s+STATIC\s+System\s+CPU$", re.MULTILINE)

    def execute_snmp(self, **kwargs):
        mac = self.snmp.get(
            "1.3.6.1.4.1.27514.1.2.1.1.1.1.0",
            display_hints={"1.3.6.1.4.1.27514.1.2.1.1.1.1.0": render_mac},
        )
        if mac is None:
            mac = self.snmp.get(
                "1.3.6.1.4.1.13464.1.2.1.1.1.1.0",
                display_hints={"1.3.6.1.4.1.13464.1.2.1.1.1.1.0": render_mac},
            )
        return {"first_chassis_mac": mac, "last_chassis_mac": mac}

    def execute_cli(self, **kwargs):
        # Fallback to CLI
        v = self.cli("show version", cached=True)
        match = self.rx_mac.search(v)
        if not match:
            v = self.cli("show mac-address-table static")
            match = self.rx_mac1.search(v)
        mac = match.group("mac")
        return {"first_chassis_mac": mac, "last_chassis_mac": mac}
