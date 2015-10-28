__author__ = 'FeNikS'
# -*- coding: utf-8 -*-

##----------------------------------------------------------------------
## Harmonic.bNSG9000.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
## Python modules
import re

rx_version = re.compile(r" SwVersion=\"(?P<ver>.*?)\"", re.DOTALL|re.MULTILINE)

class Script(BaseScript):
    name = "Harmonic.bNSG9000.get_version"
    interface = IGetVersion

    def execute(self):
        version = ''
        data = self.scripts.get_config()
        match = rx_version.search(data)
        if match:
            version = match.group("ver")

        return {
            "vendor": "Harmonic",
            "platform": "bNSG 9000",
            "version": version if version else "Unknown"
        }
