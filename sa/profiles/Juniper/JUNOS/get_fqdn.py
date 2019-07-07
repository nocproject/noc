# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Juniper.JUNOS.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.mib import mib
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "Juniper.JUNOS.get_fqdn"
    interface = IGetFQDN

    rx_config = re.compile(
        r"^host-name (?P<hostname>\S+);\s+" r"^domain-name (?P<dname>\S+);$", re.MULTILINE
    )

    def execute_snmp(self):
        fqnd = self.snmp.get(mib["SNMPv2-MIB::sysName.0"])
        return fqnd

    def execute_cli(self):
        fqdn = []
        v = self.cli("show configuration system", cached=True)
        match = self.rx_config.search(v)
        if match:
            fqdn += [match.group("hostname")]
            fqdn += [match.group("dname")]
            return ".".join(fqdn)
