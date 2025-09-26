# ---------------------------------------------------------------------
# EdgeCore.ES.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "EdgeCore.ES.get_chassis_id"
    cache = True
    interface = IGetChassisID
    rx_mac_4626 = re.compile(r"\d+\s+(?P<id>\S+).*?System\s+CPU", re.IGNORECASE | re.MULTILINE)
    rx_mac_3528mv2 = re.compile(
        r"\sMAC\sAddress\s+\(Unit\s\d\)\s+:\s+(?P<id>\S+)", re.IGNORECASE | re.MULTILINE
    )
    rx_mac = re.compile(r"MAC Address[^:]*?:\s*(?P<id>\S+)", re.IGNORECASE | re.MULTILINE)

    def execute_cli(self):
        if self.is_platform_4626:
            v = self.cli("show mac-address-table static")
            match = self.re_search(self.rx_mac_4626, v)
            mac = match.group("id")
            return {"first_chassis_mac": mac, "last_chassis_mac": mac}
        if self.is_platform_3528mv2:
            v = self.cli("show system\n")  # ES-3538MV2
            match = self.rx_mac_3528mv2.search(v)
        else:
            v = self.cli("show system", cached=True)
            match = self.re_search(self.rx_mac, v)
        first_mac = match.group("id")
        last_mac = first_mac
        return {"first_chassis_mac": first_mac, "last_chassis_mac": last_mac}
