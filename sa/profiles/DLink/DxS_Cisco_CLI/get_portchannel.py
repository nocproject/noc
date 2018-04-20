# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# DLink.DxS_Cisco_CLI.get_portchannel
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel
import re


class Script(BaseScript):
    name = "DLink.DxS_Cisco_CLI.get_portchannel"
    interface = IGetPortchannel
=======
##----------------------------------------------------------------------
## DLink.DxS_Cisco_CLI.get_portchannel
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
    name = "DLink.DxS_Cisco_CLI.get_portchannel"
    implements = [IGetPortchannel]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_line = re.compile(
        r"^AggregatePort (?P<port>\d+)\s+(up|down)\s+\d+\s+\S+\s+\S+\s+\S+$",
        re.MULTILINE)
    rx_line1 = re.compile(
        r"^\s+(?P<interface>\S+\s*\d+\/\d+)\s+Link Status: (Down|Up)$",
        re.MULTILINE)

    def execute(self):
        r = []
        data = self.cli("show interfaces status | i AggregatePort")
        for match in self.rx_line.finditer(data):
            port = int(match.group("port"))
            members = []
            data1 = self.cli(
                "show interfaces AggregatePort %i | i Link Status:" % port)
            for match1 in self.rx_line1.finditer(data1):
                members += [match1.group("interface")]
            r += [{
                "interface": "Ag %i" % port,
                "members": members,
                "type": "L"
            }]
        return r
