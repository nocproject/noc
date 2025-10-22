# ---------------------------------------------------------------------
# Cisco.IOSXR.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.mac import MAC


class Script(BaseScript):
    name = "Cisco.IOSXR.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_range = re.compile(
        r"Base MAC Address\s*:\s*(?P<mac>\S+)\s+MAC Address block size\s*:\s*(?P<count>\d+)",
        re.DOTALL | re.IGNORECASE,
    )

    def execute(self, **kwargs):
        if self.is_platform_crs16:
            # Does not work for Cisco CRS-16/S Version IOSXR 4.3.2. Impossible get chassis mac over CLI
            # must be use SNMP method
            self.always_prefer = "S"
        return super().execute(**kwargs)

    def execute_cli(self, **kwargs):
        v = self.cli("admin show diag chassis eeprom-info")
        macs = []
        for f, t in [
            (mac, MAC(mac).shift(int(count) - 1)) for mac, count in self.rx_range.findall(v)
        ]:
            if macs and MAC(f).shift(-1) == macs[-1][1]:
                macs[-1][1] = t
            else:
                macs += [[f, t]]
        return [{"first_chassis_mac": f, "last_chassis_mac": t} for f, t in macs]
