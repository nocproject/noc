# ----------------------------------------------------------------------
# Eltex.MES24xx.get_chassis_id
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Eltex.MES24xx.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac = re.compile(r"^Chassis Id\s+:\s+(?P<mac>\S+)", re.MULTILINE)
    rx_mac2 = re.compile(r"^\s+Address\s+(?P<mac>\S+)", re.MULTILINE)

    def execute_cli(self, **kwargs):
        match = self.rx_mac.search(self.cli("show lldp local"))
        # do not use `show spanning-tree switch default`
        # if stp disabled - output 00:00:00:00:00:00 mac
        if match:  # MES2428, fw 10.1.9.1 return empty string
            return {"first_chassis_mac": match.group("mac"), "last_chassis_mac": match.group("mac")}
        # Last resort
        v = self.cli("show spanning-tree")
        match = self.rx_mac2.search(v)
        if match and "This bridge is the root" in v:
            return {"first_chassis_mac": match.group("mac"), "last_chassis_mac": match.group("mac")}
        raise self.NotSupportedError()
