# ---------------------------------------------------------------------
# Cisco.SANOS.get_fqdn
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
    name = "Cisco.SANOS.get_fqdn"
    interface = IGetFQDN
    always_prefer = "S"

    rx_hostname = re.compile(r"^switchname\s+(?P<hostname>\S+)", re.MULTILINE)
    rx_domain_name = re.compile(r"^ip domain[ \-]name\s+(?P<domain>\S+)", re.MULTILINE)

    def execute_cli(self):
        v = self.cli("show running-config | i switchname")
        fqdn = []
        match = self.rx_hostname.search(v)
        if match:
            fqdn += [match.group("hostname")]
        v = self.cli("show running-config | i domain-name")
        match = self.rx_domain_name.search(v)
        if match:
            fqdn += [match.group("domain")]
        return ".".join(fqdn)
