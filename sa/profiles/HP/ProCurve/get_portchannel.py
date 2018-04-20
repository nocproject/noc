# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# HP.ProCurve.get_portchannel
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel


class Script(BaseScript):
    name = "HP.ProCurve.get_portchannel"
    interface = IGetPortchannel
=======
##----------------------------------------------------------------------
## HP.ProCurve.get_portchannel
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
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
    name = "HP.ProCurve.get_portchannel"
    implements = [IGetPortchannel]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_trunk = re.compile(r"^\s*(?P<port>\S+)\s+\|.+?\|"
                          "\s+(?P<trunk>\S+)\s+(?P<type>(\S+)?"
                          "$)", re.MULTILINE)


    def execute(self):
        r = []
        # Get trunks
        trunks = {}
        trunk_types = {}
        for port, trunk, type, pad in self.rx_trunk.findall(
                self.cli("show trunks")):
            if trunk == 'Group':
                continue
            if trunk not in trunks:
                trunks[trunk] = []
                trunk_types[trunk] = type
            trunks[trunk] += [port]
        # Build result
        for trunk in trunks:
            r += [{
                "interface": trunk,
                "members": trunks[trunk],
                "type": "L" if trunk_types[trunk].lower() == "lacp" else "S"
            }]
        return r
