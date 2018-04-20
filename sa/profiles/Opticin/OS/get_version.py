# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Opticin.OS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC Modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Opticin.OS.get_version"
    cache = True
    interface = IGetVersion
=======
##----------------------------------------------------------------------
## Opticin.OS.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC Modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion


class Script(NOCScript):
    name = "Opticin.OS.get_version"
    cache = True
    implements = [IGetVersion]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    ##
    ## Main dispatcher
    ##
    def execute(self):
        try:
            s = self.cli("show version", cached=True)
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        return self.get_version(s, None)

    ##
    ## 35xx
    ##
    rx_ver = re.compile(
        r"^\s*The system fireware version is\s+:\s*\n\s+(?P<platform>.+?)-V(?P<version>\S+)EN,",
        re.MULTILINE | re.IGNORECASE)

    def get_version(self, show_system, version):
        # Vendor default
        vendor = "Opticin"
        # Detect version & platform
        if not version:
            v = self.cli("show version", cached=True)
            match = self.re_search(self.rx_ver, v)
            version = match.group("version")
            platform = match.group("platform")
        else:
            raise self.NotSupportedError(platform)
        r = {
            "vendor": vendor,
            "platform": platform,
            "version": version,
            "attributes": {}
        }
        return r
