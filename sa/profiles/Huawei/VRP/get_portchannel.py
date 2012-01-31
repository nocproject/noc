# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP.get_portchannel
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetPortchannel
import re


class Script(noc.sa.script.Script):
    name = "Huawei.VRP.get_portchannel"
    implements = [IGetPortchannel]

    @NOCScript.match(version__startswith="3.")
    def execute_vrp3(self):
        raise self.NotSupportedError()

    rx_chan_line_vrp5 = re.compile(r"(?P<interface>Eth-Trunk\d+).*?\nWorkingMode: (?P<mode>\S+).*?\nPortName[^\n]+(?P<members>.*?)\n\n", re.IGNORECASE | re.DOTALL | re.MULTILINE)

    @NOCScript.match()
    def execute_other(self):
        r = []
        for match in self.rx_chan_line_vrp5.finditer(self.cli("display eth-trunk")):
            r += [{
                "interface": match.group("interface"),
                "members": [l.split(" ", 1)[0] for l in match.group("members").lstrip("\n").splitlines()],
                "type": {"normal": "S", "static": "L"}[match.group("mode").lower()],
            }]
        return r
