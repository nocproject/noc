# ---------------------------------------------------------------------
# Sumavision.IPQAM.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Sumavision.IPQAM.get_chassis_id"
    cache = True
    interface = IGetChassisID

    def execute_snmp(self):
        macs = [self.snmp.get("1.3.6.1.4.1.32285.2.2.10.2.2.1.1.4.0")]
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.32285.2.2.10.3008.4.2.1.7"):
            macs.append(v)
        if macs:
            return [
                {"first_chassis_mac": f, "last_chassis_mac": t}
                for f, t in self.macs_to_ranges(macs)
            ]
