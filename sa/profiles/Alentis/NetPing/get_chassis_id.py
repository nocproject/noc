# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alentis.NetPing.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------


## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID


class Script(NOCScript):
    name = "Alentis.NetPing.get_chassis_id"
    cache = True
    implements = [IGetChassisID]

    def execute(self):
        mac = self.snmp.get("1.3.6.1.2.1.2.2.1.6.1", cached=True)
        return mac
