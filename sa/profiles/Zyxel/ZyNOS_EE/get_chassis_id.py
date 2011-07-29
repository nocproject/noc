# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS_EE.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID


class Script(NOCScript):
    name = "Zyxel.ZyNOS_EE.get_chassis_id"
    cache = True
    rx_ver = re.compile(r"^\sMAC Address\s:\s+(?P<id>\S+).",
                        re.IGNORECASE | re.MULTILINE | re.DOTALL)
    implements = [IGetChassisID]

    def execute(self):
        match = self.re_search(self.rx_ver, self.cli("sys mrd atsh"))
        return match.group("id")
