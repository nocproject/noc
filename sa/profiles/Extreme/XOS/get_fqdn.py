# ---------------------------------------------------------------------
# Extreme.XOS.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_fqdn import Script as BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "Extreme.XOS.get_fqdn"
    interface = IGetFQDN
    rx_hostname = re.compile(r"^SysName:\s+(?P<hostname>\S+)", re.MULTILINE)
    rx_domain_name = re.compile(r"^ip domain[ \-]name\s+(?P<domain>\S+)", re.MULTILINE)

    always_prefer = "S"

    def execute_cli(self):
        v = self.cli("show switch | include SysName")
        fqdn = []
        match = self.rx_hostname.search(v)
        if match:
            fqdn += [match.group("hostname")]
        match = self.rx_domain_name.search(v)
        if match:
            fqdn += [match.group("domain")]
        return ".".join(fqdn)
