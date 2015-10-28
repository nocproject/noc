# -*- coding: utf-8 -*-
__author__ = 'FeNikS'
##----------------------------------------------------------------------
## Cisco.DCMD9902.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion

rx_version = re.compile(r"BUILD=(?P<ver>.*?)$",
                        re.DOTALL|re.MULTILINE)

class Script(BaseScript):
    name = "Cisco.DCM.get_version"
    interface = IGetVersion

    def execute(self):
        version = ''
        data = self.cli("cat /app/bin/versions")
        match = rx_version.search(data)
        if match:
            version = match.group("ver")

        return {
            "vendor": "Cisco",
            "platform": "DCM D9902",
            "version": version if version else "Unknown"
        }
