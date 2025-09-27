# ----------------------------------------------------------------------
# Cisco.SMB.get_fqdn
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_fqdn import Script as BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "Cisco.SMB.get_fqdn"
    interface = IGetFQDN
    rx_hostname = re.compile(r"System Name:\s+(?P<hostname>\S+)")

    def execute_cli(self):
        v = self.cli("show system")
        match = self.rx_hostname.search(v)
        return [match.group("hostname")]
