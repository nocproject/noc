# #----------------------------------------------------------------------
# Cisco.SANOS.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.mac import MAC


class Script(BaseScript):
    name = "Cisco.SANOS.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_mac = re.compile(
        r"\s+MAC\s+Addresses\s+:\s+(?P<base>\S+)\n\s+Number\s+of\s+MACs\s+:\s+(?P<count>\d+)\n",
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )

    def execute(self):
        try:
            v = self.cli("show sprom sup | include MAC")
        except self.CLISyntaxError:
            raise self.NotSupportedError()

        r = []
        for match in self.rx_mac.finditer(v):
            base = match.group("base")
            count = int(match.group("count"))
            if count == 0:
                continue
            r += [{"first_chassis_mac": base, "last_chassis_mac": MAC(base).shift(count - 1)}]

        return r
