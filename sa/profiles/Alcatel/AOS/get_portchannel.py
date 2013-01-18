# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.AOS.get_portchannel
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetPortchannel
import re


class Script(NOCScript):
    name = "Alcatel.AOS.get_portchannel"
    implements = [IGetPortchannel]
    rx_line = re.compile(
        r"^\s+(?P<port>\d+)\s+Static",
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
                "interface": "Ag %i" % port,
                "members": members,
                #<!> TODO: port-channel type detection
                "type": "L"
                }]
        return r
