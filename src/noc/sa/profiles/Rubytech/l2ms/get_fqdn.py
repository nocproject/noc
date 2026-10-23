# ---------------------------------------------------------------------
# Rubytech.l2ms.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_fqdn import Script as BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "Rubytech.l2ms.get_fqdn"
    interface = IGetFQDN
    always_prefer = "S"

    rx_hostname = re.compile(r"Device Name\s+:\s(?P<hostname>\S+)\n", re.MULTILINE)

    def execute_cli(self):
        self.cli("system")
        v = self.cli("show")

        match = self.rx_hostname.search(v)
        if match:
            return match.group("hostname")
        raise NotImplementedError
