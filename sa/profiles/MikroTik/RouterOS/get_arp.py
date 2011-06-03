# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MikroTik.RouterOS.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
""" 
""" 
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetARP
import re

class Script(NOCScript):
    name = "MikroTik.RouterOS.get_arp" 
    implements = [IGetARP]
    rx_line = re.compile(r"address=(?P<ip>\d+\.\d+\.\d+\.\d+) mac-address=(?P<mac>\S+) interface=(?P<interface>\S+)", re.MULTILINE)
    def execute(self):
        r = []
        for match in self.rx_line.finditer(self.cli("ip arp print terse")):
            r += [{
                "ip" : match.group("ip"),
                "mac" : match.group("mac"),
                "interface" : match.group("interface"),
            }]
        return r
