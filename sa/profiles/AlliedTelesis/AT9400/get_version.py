# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlliedTelesis.AT9400.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion

class Script(NOCScript):
    name = "AlliedTelesis.AT9400.get_version"
    cache = True
    implements = [IGetVersion]
    rx_ver = re.compile(r"^Model Name ...... (?P<platform>AT[/\w-]+).+^Serial Number ... (?P<serial>\S+).+^Bootloader ...... ATS63_LOADER v(?P<bootprom>\d+\.\d+\.\d+).+^Application ..... ATS63 v(?P<version>\S+(\s\S+))\s\s", re.MULTILINE | re.DOTALL)

    def execute(self):
        if self.snmp and self.access_profile.snmp_ro:
            try:
                pl = self.snmp.get("1.3.6.1.4.1.207.8.17.1.3.1.6.1")
                ver = self.snmp.get("1.3.6.1.4.1.207.8.17.1.3.1.5.1")
                return {
                    "vendor"    : "Allied Telesis",
                    "platform"  : pl,
                    "version"   : string.lstrip(ver, "v"),
                }
            except self.snmp.TimeOutError:
                pass
        match = self.rx_ver.search(self.cli("show system", cached=True))
        return {
            "vendor"  : "Allied Telesis",
            "platform": match.group("platform"),
            "version" : match.group("version"),
            "attributes" : {
                "Boot PROM" : match.group("bootprom"),
                "serial"    : match.group("serial")
            }
        }
