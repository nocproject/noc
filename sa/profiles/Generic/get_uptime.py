# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Generic.get_uptime
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetuptime import IGetUptime
from noc.lib.validators import is_float
from noc.core.mib import mib


class Script(BaseScript):
    """
    Returns system uptime in seconds
    """
    name = "Generic.get_uptime"
    interface = IGetUptime
    requires = []

    def execute(self):
        if self.has_snmp():
            try:
                su = self.snmp.get(mib["SNMPv2-MIB::sysUpTime", 0])
                # DES-1210-28/ME/B3 fw 10.04.B020 return 'VLAN-1002'
                if is_float(su):
                    return float(su) / 100.0
            except self.snmp.TimeOutError:
                pass
        return None
