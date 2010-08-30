# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.ProCurve.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetChassisID
import re

rx_mac=re.compile(r"([0-9a-f]{6}-[0-9a-f]{6})",re.IGNORECASE|re.MULTILINE|re.DOTALL)

class Script(noc.sa.script.Script):
    name="HP.ProCurve.get_chassis_id"
    implements=[IGetChassisID]
    def execute(self):
        v=self.cli("show management")
        match=rx_mac.search(v)
        return match.group(1)
