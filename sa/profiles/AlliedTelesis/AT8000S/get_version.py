# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# AlliedTelesis.AT8000S.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# coded by azhur
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re


class Script(BaseScript):
    name = "AlliedTelesis.AT8000S.get_version"
    cache = True
    interface = IGetVersion
=======
##----------------------------------------------------------------------
## AlliedTelesis.AT8000S.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## coded by azhur
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion
import re


class Script(NOCScript):
    name = "AlliedTelesis.AT8000S.get_version"
    cache = True
    implements = [IGetVersion]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_ver = re.compile(r"^\s*(?:\w*\s+){1,2}\s*(?P<version>v?[\d.]+)\s",
        re.MULTILINE | re.DOTALL)

    def execute(self):
<<<<<<< HEAD
        if self.has_snmp():
=======
        if self.snmp and self.access_profile.snmp_ro:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            try:
                ver = self.snmp.get("1.3.6.1.4.1.89.2.4.0")
                return {
                    "vendor": "Allied Telesis",
                    "platform": "AT8000S",
                    "version": ver,
                }
            except self.snmp.TimeOutError:
                pass
        v = self.cli("show version")
        match = self.rx_ver.search(v)
        return {
            "vendor": "Allied Telesis",
            "platform": "AT8000S",
            "version": match.group("version")
        }
