# ---------------------------------------------------------------------
# Angtel.Topaz.get_fqdn
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
    name = "Angtel.Topaz.get_fqdn"
    interface = IGetFQDN

    always_prefer = "S"

    rx_hostname = re.compile(r"System\sName\s*:\s*(?P<hostname>.+)")

    def execute_cli(self, **kwargs):
        v = self.cli("show system", cached=True)
        match = self.rx_hostname.search(v)
        if match:
            return match.group("hostname")
        return ""
