# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS.get_portchannel
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetPortchannel


class Script(NOCScript):
    name = "Zyxel.ZyNOS.get_portchannel"
    implements = [IGetPortchannel]

    ##
    ## 3.70 firmware
    ##
    rx_trunk_370 = re.compile(r"^Group ID\s+(?P<trunk>\d+):\s+active\s*.\s*Member number:\s+\d+\s+Member:(?P<ports>(\d+\s+)*)$", re.IGNORECASE | re.MULTILINE | re.DOTALL)

    @NOCScript.match(version__startswith="3.70")
    def execute_370(self):
        r = []
        for match in self.rx_trunk_370.finditer(self.cli("show trunk")):
            r += [{
                "interface": "T%s" % match.group("trunk"),
                "type": "L",  # @todo: type detection is not implemented yet
                "members": self.expand_rangelist(re.sub(r"\s+", ",", match.group("ports").strip()))
            }]
        return r

    ##
    ## other versions
    ##
    rx_trunk = re.compile(r"^Group ID\s+(?P<trunk>\d+):\s+active\s*.\s*Status:\s+(?P<lacp>(Static|LACP))\s*.\s*Member number:\s+\d+\s+Member:(?P<ports>(\d+\s+)*)$", re.IGNORECASE | re.MULTILINE | re.DOTALL)

    @NOCScript.match()
    def execute_other(self):
        r = []
        for match in self.rx_trunk.finditer(self.cli("show trunk")):
            r += [{
                "interface": "T%s" % match.group("trunk"),
                "type": "L" if match.group("lacp").lower() == "lacp" else "S",
                "members": self.expand_rangelist(re.sub(r"\s+", ",", match.group("ports").strip()))
            }]
        return r
