# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alentis.NetPing.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion


class Script(NOCScript):
    name = "Alentis.NetPing.get_version"
    implements = [IGetVersion]
    cache = True

    rx_snmp = re.compile(
        r"^(?P<platform1>\S+) (?P<platform2>\S+), FW v(?P<version>\S+)$")
    rx_http = re.compile(
        r"^var devname='+(?P<platform1>\S+) (?P<platform2>\S+)+'; var fwver='v+(?P<version>\S+)+';")

    def execute(self):
        # Try SNMP first
        if self.snmp and self.access_profile.snmp_ro:
            try:
                ver = self.snmp.get("1.3.6.1.2.1.1.1.0", cached=True)
                match = self.rx_snmp.search(ver)
                if match:
                    platform = "%s-%s" % (match.group("platform1"),
                                          match.group("platform2"))
                    version = match.group("version")
                return {
                        "vendor": "Alentis",
                        "platform": platform,
                        "version": version
                        }
            except self.snmp.TimeOutError:
                pass

        # Fallback to HTTP
        ver = self.http.get("/devname.cgi")
        match = self.rx_http.search(ver)
        platform = "%s-%s" % (match.group("platform1"),
                              match.group("platform2"))
        version = match.group("version")
        serial = self.http.get("/setup_get.cgi")
        serial = serial.split('serial:"SN:')[1]
        serial = serial.split(' [')[0]
        return {
                "vendor": "Alentis",
                "platform": platform,
                "version": version,
                "attributes": {
                        "Serial Number": serial
                    }
                }
