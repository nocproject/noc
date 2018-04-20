# -*- coding: utf-8 -*-
# #----------------------------------------------------------------------
<<<<<<< HEAD
# Cisco.NXOS.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.mac import MAC


class Script(BaseScript):
    name = "Cisco.NXOS.get_chassis_id"
    cache = True
    interface = IGetChassisID

=======
## Cisco.NXOS.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID
from noc.lib.mac import MAC


class Script(NOCScript):
    name = "Cisco.NXOS.get_chassis_id"
    cache = True
    implements = [IGetChassisID]

    ##
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_mac = re.compile(r"\s+MAC\s+Addresses\s+:\s+(?P<base>\S+)\n"
                        r"\s+Number\s+of\s+MACs\s+:\s+(?P<count>\d+)\n",
                        re.IGNORECASE | re.MULTILINE | re.DOTALL)

<<<<<<< HEAD
=======

>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def execute(self):
        try:
            v = self.cli("show sprom backplane | include MAC")
        except self.CLISyntaxError:
<<<<<<< HEAD
            try:
                v = self.cli("show sprom backplane 1 | include MAC")
            except self.CLISyntaxError:
                raise self.NotSupportedError()
=======
            raise self.NotSupportedError()
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        try:
            v += "\n" + self.cli("show sprom fex all | include MAC")
        except self.CLISyntaxError:
            pass

        r = []
        for match in self.rx_mac.finditer(v):
            base = match.group("base")
            count = int(match.group("count"))
            if count == 0:
                continue
            r += [{
                "first_chassis_mac": base,
                "last_chassis_mac": MAC(base).shift(count - 1)
            }]

<<<<<<< HEAD
        return r
=======
        return r
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
