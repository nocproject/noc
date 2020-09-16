# ---------------------------------------------------------------------
# Huawei.VRP.get_fqdn
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
    name = "Huawei.VRP.get_fqdn"
    interface = IGetFQDN

    always_prefer = "S"

    rx_hostname = re.compile(r"^\s*sysname\s+(?P<hostname>\S+)", re.MULTILINE)
    rx_hostname_lldp = re.compile(r"^\s*System name\s+:\s*(?P<hostname>\S+)", re.MULTILINE)
    rx_domain_name = re.compile(r"^ip domain[ \-]name\s+(?P<domain>\S+)", re.MULTILINE)

    def execute_cli(self):
        if self.has_capability("Network | LLDP"):
            try:
                v2 = self.cli("display lldp local | include System name")
                match = self.rx_hostname_lldp.search(v2)
                if match:
                    return match.group("hostname")
            except self.CLISyntaxError:
                pass

        v = self.cli("display current-configuration | include sysname")
        fqdn = []
        match = self.rx_hostname.search(v)
        if match:
            fqdn += [match.group("hostname")]
        match = self.rx_domain_name.search(v)
        if match:
            fqdn += [match.group("domain")]
        return ".".join(fqdn)
