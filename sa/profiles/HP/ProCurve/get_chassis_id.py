# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# HP.ProCurve.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
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
    name = "HP.ProCurve.get_chassis_id"
    cache = True
    interface = IGetChassisID
=======
##----------------------------------------------------------------------
## HP.ProCurve.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID


class Script(NOCScript):
    name = "HP.ProCurve.get_chassis_id"
    cache = True
    implements = [IGetChassisID]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    rx_mac = re.compile(r"([0-9a-f]{6}-[0-9a-f]{6})",
        re.IGNORECASE | re.MULTILINE | re.DOTALL)

    def execute(self):
        v = self.cli("show management")
        match = self.re_search(self.rx_mac, v)
        mac = match.group(1)
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
