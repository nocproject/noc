# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Alentis.NetPing.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Alentis.NetPing.get_version"
    interface = IGetVersion
=======
##----------------------------------------------------------------------
## Alentis.NetPing.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    cache = True

    rx_snmp = re.compile(
        r"^(?P<platform>\S+), FW v(?P<version>\S+)$")

    rx_plat = re.compile(
        r"^var devname='+(?P<platform>.+)+';$",
        re.MULTILINE)

    rx_ver = re.compile(
        r"^var fwver='v+(?P<version>\S+)+';$",
        re.MULTILINE)

    def execute(self):
        # Try SNMP first
<<<<<<< HEAD
        if self.has_snmp():
=======
        if self.snmp and self.access_profile.snmp_ro:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            try:
                ver = self.snmp.get("1.3.6.1.2.1.1.1.0", cached=True)
                match = self.rx_snmp.search(ver)
                if match:
                    platform = match.group("platform")
                    version = match.group("version")
                return {
                        "vendor": "Alentis",
                        "platform": platform,
                        "version": version
                        }
            except self.snmp.TimeOutError:
                pass

        # Fallback to HTTP
        data = self.http.get("/devname.cgi")
        match = self.rx_plat.search(data)
        platform = match.group("platform")
        match = self.rx_ver.search(data)
        version = match.group("version")

        data = self.profile.var_data(self, "/setup_get.cgi")

        return {
                "vendor": "Alentis",
                "platform": platform,
                "version": version,
                "attributes": {
                        "Serial Number": data["serialnum"]
                    }
                }
