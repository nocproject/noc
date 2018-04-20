# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Extreme.XOS.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
=======
##----------------------------------------------------------------------
## Extreme.XOS.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

rx_mac = re.compile(r"^System MAC:\s+(?P<mac>\S+)$", re.MULTILINE)


<<<<<<< HEAD
class Script(BaseScript):
    name = "Extreme.XOS.get_chassis_id"
    interface = IGetChassisID
    cache = True

=======
class Script(NOCScript):
    name = "Extreme.XOS.get_chassis_id"
    implements = [IGetChassisID]
    cache = True


>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def execute(self):
        # Fallback to CLI
        match = rx_mac.search(self.cli("show switch", cached=True))
        if match:
            mac = match.group("mac").lower()
            return {
<<<<<<< HEAD
                "first_chassis_mac": mac,
                "last_chassis_mac": mac
            }

        raise self.NotSupportedError()
=======
               "first_chassis_mac": mac,
               "last_chassis_mac": mac
            }
        else:
            return {}
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
