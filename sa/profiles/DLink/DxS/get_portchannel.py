# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# DLink.DxS.get_portchannel
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel
import re


class Script(BaseScript):
    name = "DLink.DxS.get_portchannel"
    interface = IGetPortchannel
=======
##----------------------------------------------------------------------
## DLink.DxS.get_portchannel
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetPortchannel
import re


class Script(NOCScript):
    name = "DLink.DxS.get_portchannel"
    implements = [IGetPortchannel]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_trunk = re.compile(r"Group ID\s+:\s+(?P<trunk>\d+).+?Type\s+:\s+(?P<type>\S+).+?Member Port\s+:\s+(?P<members>\S+).+?Status\s+:\s+(?P<status>\S+)", re.MULTILINE | re.DOTALL)

    def execute(self):
        try:
            t = self.cli("show link_aggregation")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        r = []
        for match in self.rx_trunk.finditer(t):
<<<<<<< HEAD
            r += [{
                "interface": "T%s" % match.group("trunk"),
                "members": self.expand_interface_range(
                    match.group("members")
                ),
                "type": "L" if match.group("type").lower() == "lacp" else "S"
            }]
=======
            if match.group("status").lower() == "enabled":
                r += [{
                    "interface": "T%s" % match.group("trunk"),
                    "members": self.expand_interface_range(
                        match.group("members")
                    ),
                    "type": "L" if match.group("type").lower() == "lacp" else "S"
                    }]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        return r
