__author__ = 'FeNikS'
# -*- coding: utf-8 -*-

##----------------------------------------------------------------------
## Harmonic.bNSG9000.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion
## Python modules
import re

rx_version = re.compile(r" SwVersion=\"(?P<ver>.*?)\"", re.DOTALL|re.MULTILINE)

class Script(NOCScript):
    name = "Harmonic.bNSG9000.get_version"
    implements = [IGetVersion]

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