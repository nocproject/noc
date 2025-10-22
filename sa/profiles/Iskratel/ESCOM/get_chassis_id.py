# ---------------------------------------------------------------------
# Iskratel.ESCOM.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Iskratel.ESCOM.get_chassis_id"
    cache = True
    interface = IGetChassisID

    # Base ethernet MAC Address - ESCOM L
    rx_mac = re.compile(r"^(System|Base ethernet) MAC Address:\s+(?P<mac>\S+)", re.MULTILINE)
    rx_mac_oob = re.compile(
        r"^System MAC Address:\s+(?P<mac>\S+)\s*\n^OOB MAC Address:\s+(?P<oob>\S+)",
        re.MULTILINE,
    )

    def execute_cli(self, **kwargs):
        if self.is_escom_l:
            v = self.cli("show version", cached=True)
        else:
            v = self.cli("show system", cached=True)
        match = self.rx_mac.search(v)
        if match:
            return {"first_chassis_mac": match.group("mac"), "last_chassis_mac": match.group("mac")}
        match = self.rx_mac_oob.search(self.cli("show system unit 1", cached=True))
        return {"first_chassis_mac": match.group("mac"), "last_chassis_mac": match.group("oob")}
