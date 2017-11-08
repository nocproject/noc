# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# OS.ESXi.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
import re

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "OS.ESXi.get_fqdn"
    interface = IGetFQDN
    rx_hostname = re.compile(r"^(?P<hostname>\S+)")

    def execute(self):
        match = self.rx_hostname.search(self.cli("hostname"))
        return match.group("hostname")
