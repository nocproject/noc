# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ----------------------------------------------------------------------
# Cisco.SMB.get_chassis_id
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Cisco.SMB.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_mac = re.compile(
        r"^System MAC Address:\s+(?P<mac>[0-9a-f:]+)\s*$",
        re.IGNORECASE | re.MULTILINE)

    def execute(self):
        v = self.cli("show system", cached=True)
        match = self.rx_mac.search(v)
=======
##----------------------------------------------------------------------
## Cisco.SMB.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
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
    name = "Cisco.SMB.get_chassis_id"
    cache = True
    implements = [IGetChassisID]

    rx_mac = re.compile(r"^System MAC Address:\s+(?P<mac>[0-9a-f:]+)\s*$", re.IGNORECASE | re.MULTILINE)

    def execute(self):
        v = self.cli("show system")
        match = self.re_search(self.rx_mac, v)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        mac = match.group("mac")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
