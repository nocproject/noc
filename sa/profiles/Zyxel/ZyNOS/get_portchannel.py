# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS.get_portchannel
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel


class Script(BaseScript):
    name = "Zyxel.ZyNOS.get_portchannel"
    interface = IGetPortchannel

    ##
    ## 3.70 firmware
    ##
    rx_trunk_370 = re.compile(r"^Group ID\s+(?P<trunk>\d+):\s+active\s*.\s*Member number:\s+\d+\s+Member:(?P<ports>(\d+\s+)*)$", re.IGNORECASE | re.MULTILINE | re.DOTALL)

    @BaseScript.match(version__startswith="3.70")
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
    rx_trunk = re.compile(
        r"^Group ID\s+T?(?P<trunk>\d+):\s+active\s*\n"
        r"(^\s*Criteria\s+:\s+\S+\s*\n)?"
        r"^\s*Status:\s+(?P<lacp>(Static|LACP))\s*\n"
        r"^\s*Member number:\s+\d+\s+Member:(?P<ports>(\d+\s+)*)\s*$",
        re.IGNORECASE | re.MULTILINE)

    @BaseScript.match()
    def execute_other(self):
        r = []
        for match in self.rx_trunk.finditer(self.cli("show trunk")):
            r += [{
                "interface": "T%s" % match.group("trunk"),
                "type": "L" if match.group("lacp").lower() == "lacp" else "S",
                "members": self.expand_rangelist(re.sub(r"\s+", ",", match.group("ports").strip()))
            }]
        return r
