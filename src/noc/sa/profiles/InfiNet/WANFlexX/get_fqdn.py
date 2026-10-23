# ---------------------------------------------------------------------
# InfiNet.WANFlexX.get_fqdn
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
    name = "InfiNet.WANFlexX.get_fqdn"
    interface = IGetFQDN
    always_prefer = "S"

    rx_hostname = re.compile(r"SysName:      \| (?P<hostname>\S+)", re.MULTILINE)

    def execute_cli(self):
        v = self.cli("lldp local")
        match = self.rx_hostname.search(v)
        if match:
            return match.group("hostname")
        raise NotImplementedError
