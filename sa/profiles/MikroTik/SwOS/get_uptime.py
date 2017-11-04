# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MikroTik.SwOS.get_snmp_get
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetuptime import IGetUptime
from noc.core.mib import mib


class Script(BaseScript):
    """
    Returns system uptime in seconds
    """
    name = "MikroTik.SwOS.get_uptime"
    interface = IGetUptime
    requires = []

    def execute(self):
        if self.has_snmp():
            try:
                su = self.snmp.get(mib["SNMPv2-MIB::sysUpTime", 0])
                if su is not None:
                    return float(su) / 100.0
            except self.snmp.TimeOutError:
                pass
        return None
