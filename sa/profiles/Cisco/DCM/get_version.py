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
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion

rx_version = re.compile(r"BUILD=(?P<ver>.*?)$",
                        re.DOTALL|re.MULTILINE)

class Script(NOCScript):
    name = "Cisco.DCM.get_version"
    implements = [IGetVersion]

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