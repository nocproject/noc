# ---------------------------------------------------------------------
# HP.Aruba.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "HP.Aruba.get_version"
    interface = IGetVersion
    cache = True

    def execute_snmp(self):
        vendor = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.12.67109120", cached=True)
        vendor = vendor.split("-")
        vendor = vendor[0]
        platform = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.13.67109120", cached=True)
        version = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.9.67109120", cached=True)
        version = version.split("Aruba")
        version = version[0]
        hardware = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.8.67109120", cached=True)
        serial = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.11.67109120", cached=True)

        # vendor = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.12.1",
        #                         cached=True)
        # plat = self.snmp.get("1.3.6.1.2.1.1.1.0", cached=True)
        # plat = plat.split(" ")
        # platform = plat[1]
        # vendor = plat[0]
        # version = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.9.1", cached=True)
        # bootprom = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.10.1", cached=True)
        # hardware = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.8.1", cached=True)
        # serial = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.11.1", cached=True)
        return {
            "vendor": vendor,
            "platform": platform,
            "version": version,
            "attributes": {
                # "Boot PROM": bootprom,
                "HW version": hardware,
                "Serial Number": serial,
            },
        }
