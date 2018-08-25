# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Generic.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.mac import MAC
from noc.core.mib import mib


class Script(BaseScript):
    name = "Generic.get_chassis_id"
    cache = True
    interface = IGetChassisID

    OIDS_CHECK = [mib["LLDP-MIB::lldpLocChassisId"] + ".0",
                  mib["BRIDGE-MIB::dot1dBaseBridgeAddress"] + ".0"]

    def execute_snmp(self):
        # OIDs for LLDP and STP
        r = []
        if self.has_snmp():
            for o in self.OIDS_CHECK:
                try:
                    s = self.snmp.get(o)
                except self.snmp.TimeOutError:
                    s = None
                if s is None:
                    continue
                r += [{"first_chassis_mac": MAC(s), "last_chassis_mac": MAC(s)}]
            return r
        else:
            raise self.NotSupportedError
