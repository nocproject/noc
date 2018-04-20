# -*- coding: utf-8 -*-
<<<<<<< HEAD
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
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    """
    Returns system uptime in seconds
    """
    name = "Generic.get_uptime"
<<<<<<< HEAD
    interface = IGetUptime
    requires = []

    def execute(self):
        if self.has_snmp():
            try:
                su = self.snmp.get(mib["SNMPv2-MIB::sysUpTime", 0])
                # DES-1210-28/ME/B3 fw 10.04.B020 return 'VLAN-1002'
                if is_float(su):
                    return float(su) / 100.0
=======
    implements = [IGetUptime]
    requires = []

    def execute(self):
        if self.snmp and self.access_profile.snmp_ro:
            try:
                su = self.snmp.get(mib["SNMPv2-MIB::sysUpTime", 0])
                return float(su) / 100.0
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            except self.snmp.TimeOutError:
                pass
        return None
