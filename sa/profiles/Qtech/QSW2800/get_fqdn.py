# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QSW2800.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN
from noc.core.mib import mib


class Script(BaseScript):
    name = "Qtech.QSW2800.get_fqdn"
    interface = IGetFQDN
    always_prefer = "S"

    rx_hostname = re.compile(r"^hostname (?P<hostname>\S+)$", re.MULTILINE)

    def execute_snmp(self, **kwargs):
        try:
            fqnd = self.snmp.get(mib["SNMPv2-MIB::sysName.0"])
            return fqnd
        except self.snmp.TimeOutError:
            raise NotImplementedError()

    def execute_cli(self):
        # Getting pattern prompt
        v = self.get_cli_stream()
        pattern = v.patterns["prompt"].pattern
        fqdn = pattern.split("(?")[0][1:].replace("\\", "")
        return fqdn
