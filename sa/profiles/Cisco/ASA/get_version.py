# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.ASA.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(NOCScript):
    name = "Cisco.ASA.get_version"
    cache = True
    implements = [IGetVersion]
    rx_ver = re.compile(
        r"Cisco (?:Adaptive|PIX) Security Appliance Software Version (?P<version>\S+)"
        r".+System image file is \".+?:/(?P<image>.+?)\""
        r".+Hardware:\s+(?P<platform>.+?),",
        re.MULTILINE | re.DOTALL
    )

    def execute(self):
        v = self.cli("show version")
        match = self.re_search(self.rx_ver, v)
        return {
            "vendor": "Cisco",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {
                "image": match.group("image"),
            }
        }
