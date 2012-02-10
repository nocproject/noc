# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetChassisID
import re

rx_chassis_id = re.compile(r"Ethernet Address\s+:\s*(?P<id>\S+)",
    re.IGNORECASE | re.MULTILINE)


class Script(noc.sa.script.Script):
    name = "Zyxel.ZyNOS.get_chassis_id"
    cache = True
    implements = [IGetChassisID]

    def execute(self):
        v = self.cli("show system-information")
        match = rx_chassis_id.search(v)
        return match.group("id")
