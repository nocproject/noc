# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Cisco.SMB.get_fqdn
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.mib import mib
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "Cisco.SMB.get_fqdn"
    interface = IGetFQDN
    rx_hostname = re.compile(r"System Name:\s+(?P<hostname>\S+)")

    def execute_cli(self):
        v = self.cli("show system")
        match = self.rx_hostname.search(v)
        fqdn = [match.group("hostname")]
        return fqdn

    def execute_snmp(self):
        v = self.snmp.get(mib["SNMPv2-MIB::sysName.0"], cached=True)
        if v:
            return v
