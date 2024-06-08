# ---------------------------------------------------------------------
# Telecom.CPE.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2023-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript


class Script(BaseScript):
    name = "Telecom.CPE.get_capabilities"
    cache = True
    re_about = re.compile(
        r"mode - (?P<mode>.+) channel - (?P<channel>.+) frequency - (?P<frequency>.+) GHz bit_rate - (?P<bit_rate>.+) MBit/s rssi - (?P<rssi>.+) dBm width - (?P<width>.+) MHz",
        re.IGNORECASE,
    )

    def execute_platform_snmp(self, caps):
        about = self.snmp.get("1.3.6.1.2.1.1.52.1.0")
        match = self.re_about.match(about)
        if match:
            mode, channel, frequency, bit_rate, rssi, width = match.groups()
            if width is not None:
                caps["Radio | Width"] = width
            if mode is not None:
                caps["Radio | Mode"] = mode
            if frequency is not None:
                caps["Radio | Frequency"] = int(float(frequency) * 1000)
