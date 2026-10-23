# ---------------------------------------------------------------------
# Eltex.DSLAM.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Eltex.DSLAM.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac1 = re.compile(r"^Unicast MAC table: port cpu\s*\n^(?P<mac>\S+)", re.MULTILINE)
    rx_mac2 = re.compile(r"(?P<mac>\S{17}) \[(?P<interface>.{4})\]")
    rx_mac3 = re.compile(r"MAC address: (?P<mac>\S{17})")

    def execute(self):
        try:
            cmd = self.cli("switch show mac table cpu", cached=True)
        except self.CLISyntaxError:
            cmd = self.cli("cpu show net settings", cached=True)
        match = self.rx_mac1.search(cmd)
        if match:
            mac = match.group("mac")
            return {"first_chassis_mac": mac, "last_chassis_mac": mac}
        for match in self.rx_mac2.finditer(cmd):
            interface = match.group("interface").strip()
            if interface == "cpu":
                mac = match.group("mac")
                return {"first_chassis_mac": mac, "last_chassis_mac": mac}
        match = self.rx_mac3.search(cmd)
        if match:
            mac = match.group("mac")
            return {"first_chassis_mac": mac, "last_chassis_mac": mac}
        return []
