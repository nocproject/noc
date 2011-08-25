# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlliedTelesis.AT9900.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
import string
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion


class Script(NOCScript):
    name = "AlliedTelesis.AT9900.get_version"
    cache = True
    implements = [IGetVersion]
    rx_ver = re.compile(r"^Allied Telesis (?P<platform>AT[/\w-]+) version (?P<version>[\d.]+-[\d]+)", re.MULTILINE | re.DOTALL)

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
        v = self.cli("show system")
        match = self.re_search(self.rx_ver, v)
        return {
            "vendor"  : "Allied Telesis",
            "platform": match.group("platform"),
            "version" : match.group("version"),
        }
