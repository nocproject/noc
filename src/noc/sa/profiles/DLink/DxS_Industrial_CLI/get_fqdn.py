# ---------------------------------------------------------------------
# DLink.DxS_Industrial_CLI.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "DLink.DxS_Industrial_CLI.get_fqdn"
    interface = IGetFQDN

    rx_hostname = re.compile(r"^\s*Name\s*:\s*(?P<hostname>\S+)", re.MULTILINE)

    def execute(self):
        v = self.cli("show snmp-server | include Name")
        match = self.rx_hostname.search(v)
        if match:
            return match.group("hostname")
        return "None"
