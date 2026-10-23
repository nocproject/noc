# ---------------------------------------------------------------------
# Eltex.MES5448.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from noc.sa.profiles.Generic.get_fqdn import Script as BaseScript

# NOC modules
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "Eltex.MES5448.get_fqdn"
    interface = IGetFQDN

    rx_hostname = re.compile(r"^hostname (?P<hostname>\S+)$", re.MULTILINE)
    rx_domain_name = re.compile(r"^ip domain name (?P<domain>\S+)$", re.MULTILINE)

    def execute_cli(self):
        fqdn = ""
        v = self.cli("show startup-config", cached=True)
        match = self.rx_hostname.search(v)
        if match:
            fqdn = match.group("hostname").strip('"')
            match = self.rx_domain_name.search(v)
            if match:
                fqdn = fqdn + "." + match.group("domain")
        return fqdn
