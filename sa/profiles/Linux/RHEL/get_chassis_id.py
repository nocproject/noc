# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Linux.RHEL.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Linux.RHEL.get_chassis_id"
    cache = True
    interface = IGetChassisID

    def execute(self):
        # Try SNMP first
        if self.snmp:
            try:
                mac = self.snmp.get("1.3.6.1.2.1.2.2.1.6.2", cached=True)
                if mac is not None:
                    return {
                        "first_chassis_mac": mac,
                        "last_chassis_mac": mac
                    }
                else:
                    return [{
                        "first_chassis_mac": "00:00:00:00:00:00",
                        "last_chassis_mac": "00:00:00:00:00:00"
                    }]

            except self.snmp.TimeOutError:
                pass
                return
