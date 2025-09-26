# ---------------------------------------------------------------------
# Sumavision.IPQAM.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Sumavision.IPQAM.get_version"
    interface = IGetVersion

    def execute(self):
        platform = self.snmp.get("1.3.6.1.4.1.32285.2.2.10.1.4.0")
        version = self.snmp.get("1.3.6.1.4.1.32285.2.2.10.2.1.1.0")
        bspversion = self.snmp.get("1.3.6.1.4.1.32285.2.2.10.2.1.2.0")
        fpgaversion = self.snmp.get("1.3.6.1.4.1.32285.2.2.10.2.1.3.0")
        hwversion = self.snmp.get("1.3.6.1.4.1.32285.2.2.10.2.1.4.0")
        serial_number = self.snmp.get("1.3.6.1.4.1.32285.2.2.10.2.1.5.0")

        return {
            "vendor": "Sumavision",
            "version": version.rstrip("\x00"),
            "platform": platform.rstrip("\x00"),
            "attributes": {
                "HW version": hwversion.rstrip("\x00"),
                "FPGA version": fpgaversion.rstrip("\x00"),
                "BSP version": bspversion.rstrip("\x00"),
                "Serial Number": serial_number.rstrip("\x00"),
            },
        }
