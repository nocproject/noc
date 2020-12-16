# ---------------------------------------------------------------------
# Eltex.TAU.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.mac import MAC


class Script(BaseScript):
    name = "Eltex.TAU.get_chassis_id"
    interface = IGetChassisID
    cache = True
    always_prefer = "C"

    # Working only on TAU-36
    SNMP_GET_OIDS = {"SNMP": ["1.3.6.1.4.1.35265.4.15.0"]}

    rx_shell_mac = re.compile(r"^(?:Factory|LAN) MAC: (?P<mac>\S+)", re.MULTILINE)
    rx_shell_mac_tau8 = re.compile(r"^(?P<mac>\S+)$")

    def execute_cli(self):
        if self.is_tau4:
            c = self.cli("cat /tmp/.board_desc", cached=True)
            match = self.rx_shell_mac.search(c)
        elif self.is_tau8:
            c = self.cli("cat /tmp/board_mac", cached=True)
            match = self.rx_shell_mac_tau8.search(c)
        else:
            c = self.cli("cat /tmp/factory", cached=True)
            match = self.rx_shell_mac.search(c)
        s = match.group("mac")
        return {"first_chassis_mac": MAC(s), "last_chassis_mac": MAC(s)}
