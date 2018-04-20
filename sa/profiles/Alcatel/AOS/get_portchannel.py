# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ----------------------------------------------------------------------
# Alcatel.AOS.get_portchannel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel
import re


class Script(BaseScript):
    name = "Alcatel.AOS.get_portchannel"
    interface = IGetPortchannel
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_line = re.compile(
        r"^\s+(?P<port>\d+)\s+(Static|Dynamic)",
        re.MULTILINE)
    rx_line1 = re.compile(
        r"\s+(?P<interface>\d+\/\d+)\s+\S+\s+",
        re.MULTILINE)
<<<<<<< HEAD
    rx_line2 = re.compile(
        r"^\s+(?P<interface>\d+\/\d+)\s+\S+\s+\d+\s+\S+\s+(?P<port>\d+)",
        re.MULTILINE)
=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self):
        r = []
        data = self.cli("show linkagg")
<<<<<<< HEAD
        data1 = ""
        for match in self.rx_line.finditer(data):
            port = int(match.group("port"))
            members = []
            if self.match_version(version__gte="6.3.4"):
                data1 = self.cli("show linkagg %i port" % port)
                for match1 in self.rx_line1.finditer(data1):
                    members += [match1.group("interface")]
            else:
                if not data1:
                    data1 = self.cli("show linkagg port")
                for match1 in self.rx_line2.finditer(data1):
                    if int(match1.group("port")) == port:
                        members += [match1.group("interface")]
            r += [{
                "interface": "%i" % port,
                "members": members,
                # <!> TODO: port-channel type detection
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                "type": "L"
            }]
        return r
