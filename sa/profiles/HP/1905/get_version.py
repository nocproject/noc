# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.1905.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion


class Script(NOCScript):
    name = "HP.1905.get_version"
    implements = [IGetVersion]
    cache = True

    def execute(self):
        # Try SNMP first
        print 1
        if self.snmp and self.access_profile.snmp_ro:
            try:
                vendor = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.12.1",
                                        cached=True)
                plat = self.snmp.get("1.3.6.1.2.1.1.1.0", cached=True)
                plat = plat.split(' ')
                platform = plat[1]
                vendor = plat[0]
                version = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.9.1",
                                        cached=True)
                bootprom = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.10.1",
                                         cached=True)
                hardware = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.8.1",
                                         cached=True)
                serial = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.11.1",
                                       cached=True)
                return {
                        "vendor": vendor,
                        "platform": platform,
                        "version": version,
                        "attributes": {
                            "Boot PROM": bootprom,
                            "HW version": hardware,
                            "Serial Number": serial
                            }
                        }
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        raise Exception("Not implemented")
