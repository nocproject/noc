# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Generic.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.mac import MAC
from noc.core.mib import mib
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Generic.get_chassis_id"
    cache = True
    interface = IGetChassisID

    def execute_snmp(self):
        # OIDs for LLDP and STP
        oids = [mib["LLDP-MIB::lldpLocChassisId"], mib["BRIDGE-MIB::dot1dBaseBridgeAddress"]]
        r = []
        if self.has_snmp():
            for o in oids:
                s = self.snmp.get(o + ".0")
                r += [{"first_chassis_mac": MAC(s), "last_chassis_mac": MAC(s)}]
            return r
        else:
            raise self.NotSupportedError
