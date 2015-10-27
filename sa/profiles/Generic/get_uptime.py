# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generic.get_snmp_get
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetuptime import IGetUptime
from noc.lib.mib import mib


class Script(NOCScript):
    """
    Returns system uptime in seconds
    """
    name = "Generic.get_uptime"
    implements = [IGetUptime]
    requires = []

    def execute(self):
        if self.has_snmp():
            try:
                su = self.snmp.get(mib["SNMPv2-MIB::sysUpTime", 0])
                return float(su) / 100.0
            except self.snmp.TimeOutError:
                pass
        return None
