# ---------------------------------------------------------------------
# Cisco.IOSXR.get_fqdn
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
    name = "Cisco.IOSXR.get_fqdn"
    interface = IGetFQDN
    always_prefer = "S"

    rx_hostname = re.compile(r"^hostname\s+(?P<hostname>\S+)", re.MULTILINE)
    rx_domain_name = re.compile(r"^domain name\s+(?P<domain>\S+)", re.MULTILINE)

    def execute_cli(self):
        v = self.cli('show running-config | include "hostname|domain name "')
        fqdn = []
        match = self.rx_hostname.search(v)
        if match:
            fqdn += [match.group("hostname")]
        match = self.rx_domain_name.search(v)
        if match:
            fqdn += [match.group("domain")]
        return ".".join(fqdn)
