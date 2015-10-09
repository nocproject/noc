__author__ = 'FeNikS'
# -*- coding: utf-8 -*-

##----------------------------------------------------------------------
## Harmonic.DiviComElectra.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion

rx_version = re.compile(r" CodeVersion=\"(?P<ver>.*?)\"", re.DOTALL|re.MULTILINE)

class Script(NOCScript):
    name = "Harmonic.DiviComElectra.get_version"
    implements = [IGetVersion]

    def execute(self):
        version = ''
        try:
            data = self.scripts.get_config()
            match = rx_version.search(data)
            if match:
                version = match.group("ver")
        except Exception:
            pass

        return {
            "vendor": "Harmonic",
            "platform": "DiviComElectra",
            "version": version if version else "Unknown"
        }