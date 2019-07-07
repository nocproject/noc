# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# InfiNet.WANFlexX.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "InfiNet.WANFlexX.get_fqdn"
    interface = IGetFQDN

    rx_hostname = re.compile(r"SysName:      \| (?P<hostname>\S+)", re.MULTILINE)

    def execute(self):
        if self.has_snmp():
            try:
                # sysName.0
                v = self.snmp.get("1.3.6.1.2.1.1.5.0", cached=True)
                if v:
                    return v
            except self.snmp.TimeOutError:
                pass
        v = self.cli("lldp local")

        match = self.rx_hostname.search(v)
        if match:
            fqdn = match.group("hostname")
            return fqdn
        else:
            raise self.UnexpectedResultError()
