# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vyatta.Vyatta.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.mib import mib


class Script(BaseScript):
    name = "Vyatta.Vyatta.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"^Version:\s+(?P<version>(?:VyOS )?\S+)",
        re.MULTILINE
    )
    rx_snmp_ver = re.compile(
        r"^Vyatta\s+(?P<version>(?:VyOS )?\S+)$"
    )

    def execute(self):
        version = None
        if self.has_snmp():
            try:
                v = self.snmp.get(mib["SNMPv2-MIB::sysDescr", 0])
                match = self.re_match(self.rx_snmp_ver, v)
                version = match.group("version")
            except self.snmp.TimeOutError:
                pass  # Fallback to CLI

        if not version:
            v = self.cli("show version")
            match = self.re_search(self.rx_ver, v)
            version = match.group("version")

        if "VyOS" in version:
            vendor, version = version.split(" ")
            platform = "VyOS"
        else:
            vendor = "Vyatta"
            platform = "VC"
        return {
            "vendor": vendor,
            "platform": platform,
            "version": version
        }
=======
##----------------------------------------------------------------------
## Vyatta.Vyatta.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion
##
## Vyatta.Vyatta.get_version
##
class Script(NOCScript):
    name="Vyatta.Vyatta.get_version"
    cache=True
    implements=[IGetVersion]
    
    rx_ver=re.compile(r"^Version:\s+(?P<version>\S+)",re.MULTILINE)
    def execute(self):
        v=self.cli("show version")
        match=self.re_search(self.rx_ver, v)
        return {
            "vendor"    : "Vyatta",
            "platform"  : "VC",
            "version"   : match.group("version"),
        }
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
