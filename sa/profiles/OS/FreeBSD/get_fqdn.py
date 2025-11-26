# ---------------------------------------------------------------------
# OS.FreeBSD.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "OS.FreeBSD.get_fqdn"
    interface = IGetFQDN
    rx_hostname = re.compile(r"^(?P<hostname>\S+)")

    def execute(self):
        match = self.rx_hostname.search(self.cli("hostname"))
        return match.group("hostname")
