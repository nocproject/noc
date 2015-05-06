# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP.get_portchannel
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetPortchannel
import re


class Script(NOCScript):
    name = "Huawei.VRP.get_portchannel"
    implements = [IGetPortchannel]

    @NOCScript.match(version__startswith="3.")
    def execute_vrp3(self):
        raise self.NotSupportedError()

    rx_chan_line_vrp5 = re.compile(
        r"(?P<interface>Eth-Trunk\d+).*?\n"
        r"(?:LAG ID: \d+\s+)?WorkingMode: (?P<mode>\S+).*?\n"
        r"(?:Actor)?PortName[^\n]+(?P<members>.*?)(\n\s*\n|\n\s\s)",
        re.IGNORECASE | re.DOTALL | re.MULTILINE)

    @NOCScript.match()
    def execute_other(self):
        r = []
        try:
            trunk = self.cli("display eth-trunk", cached=True)
        except self.CLISyntaxError:
            # version 5.3 produce like this:
            # Error: No valid trunk in the system.
            return []
        for match in self.rx_chan_line_vrp5.finditer(trunk):
            r += [{
                "interface": match.group("interface"),
                "members": [l.split(" ", 1)[0] for l in match.group("members").lstrip("\n").splitlines()],
                "type": {
                    "normal": "S",
                    "static": "L",
                    "lacp": "L"
                }[match.group("mode").lower()]
            }]
        return r
