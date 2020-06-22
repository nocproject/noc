# ---------------------------------------------------------------------
# Siklu.EH.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_fqdn import Script as BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "Siklu.EH.get_fqdn"
    interface = IGetFQDN
    rx_hostname = re.compile(r"^system\sname\s+:\s*(?P<hostname>\S+)\n", re.MULTILINE)

    always_prefer = "S"

    def execute_cli(self, **kwargs):
        v = self.cli("show system")
        fqdn = []
        match = self.rx_hostname.search(v)
        if match:
            fqdn += [match.group("hostname")]
        return ".".join(fqdn)
