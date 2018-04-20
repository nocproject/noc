# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# HP.ProCurve9xxx.get_chassis_id
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
    name = "HP.ProCurve9xxx.get_chassis_id"
    interface = IGetChassisID
=======
##----------------------------------------------------------------------
## HP.ProCurve9xxx.get_chassis_id
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
    name = "HP.ProCurve9xxx.get_chassis_id"
    implements = [IGetChassisID]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_mac = re.compile(r"([0-9a-f]{4}.[0-9a-f]{4}.[0-9a-f]{4})",
        re.IGNORECASE | re.MULTILINE | re.DOTALL)

    def execute(self):
        v = self.cli("show chassis")
        match = self.re_search(self.rx_mac, v)
        mac = match.group(1)
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
