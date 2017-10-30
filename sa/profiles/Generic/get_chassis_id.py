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


class Script(BaseScript):
    name = "Generic.get_chassis_id"
    cache = True
    interface = IGetChassisID

    def execute_snmp(self):
        # OIDs for LLDP and STP
        oids = ["1.0.8802.1.1.2.1.3.2.0", "1.3.6.1.2.1.17.1.1.0"]
        r = []
        if self.has_snmp():
            for o in oids:
                s = self.snmp.get(o)
                r += [{"first_chassis_mac": MAC(s), "last_chassis_mac": MAC(s)}]
            return r
        else:
            raise self.NotSupportedError
