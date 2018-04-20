# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# AlliedTelesis.AT9900
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "AlliedTelesis.AT9900.get_chassis_id"
    cache = True
    interface = IGetChassisID
    rx_ver = re.compile(
        r" Switch Address \.+ (?P<id>\S+)", re.IGNORECASE | re.MULTILINE)

    def execute(self):
        match = self.re_search(
            self.rx_ver, self.cli("show switch", cached=True)
        )
=======
##----------------------------------------------------------------------
## AlliedTelesis.AT9900
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID


class Script(NOCScript):
    name = "AlliedTelesis.AT9900.get_chassis_id"
    cache = True
    implements = [IGetChassisID]
    rx_ver = re.compile(r" Switch Address \.+ (?P<id>\S+)", re.IGNORECASE | re.MULTILINE)

    def execute(self):
        match = self.re_search(self.rx_ver, self.cli("show switch", cached=True))
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        return match.group("id")
