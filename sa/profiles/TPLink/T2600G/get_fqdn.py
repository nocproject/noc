# ---------------------------------------------------------------------
# TPLink.T2600G.get_config
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
    name = "TPLink.T2600G.get_fqdn"
    interface = IGetFQDN

    rx_hostname = re.compile(r"^hostname\s+\"(?P<hostname>\S+)\"", re.MULTILINE)
    rx_domain_name = re.compile(r"^ip domain[ \-]name\s+(?P<domain>\S+)", re.MULTILINE)

    def execute_cli(self):
        v = self.cli("show running-config | include hostname")
        fqdn = []
        match = self.rx_hostname.search(v)
        if match:
            fqdn += [match.group("hostname")]
        return ".".join(fqdn)
