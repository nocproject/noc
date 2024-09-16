# ---------------------------------------------------------------------
# Zhone.Bitstorm.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.mac import MAC


class Script(BaseScript):
    name = "Zhone.Bitstorm.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_ver = re.compile(
        r"^FW Rev\s*(?P<version>\S+)\n"
        r"^Model\s*(?P<platform>\S+)\n"
        r"^Serial Number\s*(?P<serial>\S+)\n"
        r"^MAC Address Eth1\s*(?P<mac1>\S+)\n"
        r"^MAC Address Eth2\s*(?P<mac2>\S+)\n",
        re.MULTILINE | re.IGNORECASE,
    )
    rx_mac = re.compile(
        r"^MAC Address\s+(?P<mac>\S+)\s*\n^MAC Address block size\s+(?P<count>\d+)\s*\n",
        re.MULTILINE,
    )

    def execute_cli(self):
        v = self.cli("show system information", cached=True)
        match = self.rx_ver.search(v)
        if match:
            return {
                "first_chassis_mac": match.group("mac1"),
                "last_chassis_mac": match.group("mac2"),
            }
        elif "Paradyne DSLAM" in v or "Zhone DSLAM" in v:
            v = self.cli("show slot-information", cached=True)
            match = self.rx_mac.search(v)
            base = match.group("mac")
            count = int(match.group("count"))
            return [{"first_chassis_mac": base, "last_chassis_mac": MAC(base).shift(count - 1)}]
        else:
            return {}
