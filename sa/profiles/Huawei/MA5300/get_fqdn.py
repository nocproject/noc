# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.MA5300.get_fqdn
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
    name = "Huawei.MA5300.get_fqdn"
    interface = IGetFQDN

    rx_hostname = re.compile(r"hostname\s+(?P<hostname>\S+)", re.MULTILINE)

    def execute_snmp(self):
        v = self.snmp.get("1.3.6.1.2.1.1.5.0", cached=True)
        return v

    def execute_cli(self):
        v = self.cli("show running-config configuration config")
        match = self.re_search(self.rx_hostname, v)
        if match:
            fqdn = match.group("hostname")
            return fqdn
