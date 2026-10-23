# ---------------------------------------------------------------------
# Huawei.MA5300.get_fqdn
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
    name = "Huawei.MA5300.get_fqdn"
    interface = IGetFQDN

    always_prefer = "S"

    rx_hostname = re.compile(r"hostname\s+(?P<hostname>\S+)", re.MULTILINE)

    def execute_cli(self):
        v = self.cli("show all-config | include hostname")
        match = self.re_search(self.rx_hostname, v)
        if match:
            return match.group("hostname")
