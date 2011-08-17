# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alentis.NetPing.get_version
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
    name = "Alentis.NetPing.get_version"
    cache = True
    implements = [IGetVersion]

    rx_version = re.compile(r"^(?P<platform1>\S+) (?P<platform2>\S+), FW v(?P<version>\S+)$")

    def execute(self):
        platform = "-"
        version = "-"
        if self.snmp and self.access_profile.snmp_ro:
            try:
                ver = self.snmp.get("1.3.6.1.2.1.1.1.0", cached=True)
                match = self.rx_version.search(ver)
                if match:
                    platform = "%s-%s" % (match.group("platform1"),
                                          match.group("platform2"))
                    version = match.group("version")
            except self.snmp.TimeOutError:
                pass
        return {
            "vendor": "Alentis",
            "platform": platform,
            "version": version
        }
