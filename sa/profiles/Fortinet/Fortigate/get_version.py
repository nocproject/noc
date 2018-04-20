# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Fortinet.Fortigate.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Fortinet.Fortigate.get_version"
    cache = True
    interface = IGetVersion
=======
##----------------------------------------------------------------------
## Fortinet.Fortigate.get_version
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
    name = "Fortinet.Fortigate.get_version"
    cache = True
    implements = [IGetVersion]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_ver = re.compile(r"Version:\s+(?P<platform>\S+)+\ (?P<version>\S+)",
                        re.MULTILINE | re.DOTALL)
    rx_snmp_ver = re.compile(r"(?P<platform>\S+)+\ (?P<version>\S+)")

    def execute(self):
<<<<<<< HEAD
        if self.has_snmp():
=======
        if self.snmp and self.access_profile.snmp_ro:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            try:
                v = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.10.1", cached=True)
                match = self.re_search(self.rx_snmp_ver, v)
                return {
                    "vendor": "Fortinet",
                    "platform": match.group("platform"),
                    "version": match.group("version")
                }
            except self.snmp.TimeOutError:
                pass
        v = self.cli("get system status")
        match = self.re_search(self.rx_ver, v)
        return {
            "vendor": "Fortinet",
            "platform": match.group("platform"),
            "version": match.group("version"),
        }
