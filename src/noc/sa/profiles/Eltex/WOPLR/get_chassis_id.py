# ---------------------------------------------------------------------
# Eltex.WOPLR.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Eltex.WOPLR.get_chassis_id"
    interface = IGetChassisID

    rx_mac_wan = re.compile(r"^\s*factory-wan-mac\s*(\||:)\s*(?P<wan_mac>\S+)", re.MULTILINE)
    rx_mac_lan = re.compile(r"^\s*factory-lan-mac\s*(\||:)\s*(?P<lan_mac>\S+)", re.MULTILINE)

    def execute_cli(self, **kwargs):
        d = self.cli("monitoring information", cached=True)
        match = self.rx_mac_wan.search(d)
        wan_mac = match.group("wan_mac")

        match = self.rx_mac_lan.search(d)
        lan_mac = match.group("lan_mac")
        return [{"first_chassis_mac": wan_mac, "last_chassis_mac": lan_mac}]
