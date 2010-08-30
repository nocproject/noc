# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Force10.FTOS.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetChassisID
import re

rx_id=re.compile(r"Chassis MAC\s+:\s*(?P<id>\S+)",re.IGNORECASE|re.MULTILINE)

class Script(noc.sa.script.Script):
    name="Force10.FTOS.get_chassis_id"
    implements=[IGetChassisID]
    def execute(self):
        v=self.cli("show chassis brief")
        match=rx_id.search(v)
        return match.group("id")
