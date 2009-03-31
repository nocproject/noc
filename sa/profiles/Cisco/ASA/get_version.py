# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.ASA.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
import re

#rx_ver=re.compile(r'Cisco (?:Adaptive|PIX) Security Appliance Software Version (?P<version>\S+).+System image file is ".*?:/(P<image>[^"]+)".+Hardware:\s+(?P<platform>[^,]+),',re.MULTILINE|re.DOTALL)
rx_ver=re.compile(r'Cisco (?:Adaptive|PIX) Security Appliance Software Version (?P<version>\S+).+System image file is ".+?:/(?P<image>.+?)".+Hardware:\s+(?P<platform>.+?),',re.MULTILINE|re.DOTALL)


class Script(noc.sa.script.Script):
    name="Cisco.ASA.get_version"
    implements=[IGetVersion]
    def execute(self):
        self.cli("terminal pager 0")
        v=self.cli("show version")
        match=rx_ver.search(v)
        return {
            "vendor"    : "Cisco",
            "platform"  : match.group("platform"),
            "version"   : match.group("version"),
            "image"     : match.group("image"),
        }
