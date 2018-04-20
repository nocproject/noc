# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Huawei.VRP.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Huawei.VRP.get_chassis_id"
    cache = True
    interface = IGetChassisID
=======
##----------------------------------------------------------------------
## Huawei.VRP.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetChassisID


class Script(noc.sa.script.Script):
    name = "Huawei.VRP.get_chassis_id"
    cache = True
    implements = [IGetChassisID]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_mac = re.compile(r"MAC address[^:]*?:\s*(?P<id>\S+)",
        re.IGNORECASE | re.MULTILINE)
    rx_mac1 = re.compile(r"CIST Bridge\s+:\d+\s*\.(?P<id>\S+)",
        re.IGNORECASE | re.MULTILINE)

    def execute(self):
        v = self.cli("display stp")
        match = self.rx_mac.search(v)
        if match:
            mac = match.group("id")
            return {
                "first_chassis_mac": mac,
                "last_chassis_mac": mac
            }
        else:
            match = self.rx_mac1.search(v)
            if match:
                mac = match.group("id")
                return {
                    "first_chassis_mac": mac,
                    "last_chassis_mac": mac
                }

        raise self.NotSupportedError()
