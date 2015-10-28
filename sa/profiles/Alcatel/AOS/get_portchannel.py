# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.AOS.get_portchannel
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel
import re


class Script(BaseScript):
    name = "Alcatel.AOS.get_portchannel"
    interface = IGetPortchannel
    rx_line = re.compile(
        r"^\s+(?P<port>\d+)\s+(Static|Dynamic)",
        re.MULTILINE)
    rx_line1 = re.compile(
        r"\s+(?P<interface>\d+\/\d+)\s+\S+\s+",
        re.MULTILINE)

    def execute(self):
        r = []
        data = self.cli("show linkagg")
        for match in self.rx_line.finditer(data):
            port = int(match.group("port"))
            members = []
            data1 = self.cli(
                "show linkagg %i port" % port)
            for match1 in self.rx_line1.finditer(data1):
                members += [match1.group("interface")]
            r += [{
                "interface": "%i" % port,
                "members": members,
                #<!> TODO: port-channel type detection
                "type": "L"
            }]
        return r
