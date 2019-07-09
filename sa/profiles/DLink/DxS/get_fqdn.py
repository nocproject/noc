# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DxS.get_fqdn
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
    name = "DLink.DxS.get_fqdn"
    interface = IGetFQDN

    rx_name = re.compile(r"^System [Nn]ame\s+:(?P<name>.*)$", re.MULTILINE)

    def execute_snmp(self):
        return self.snmp.get(mib["SNMPv2-MIB::sysName.0"])

    def execute_cli(self):
        v = self.scripts.get_switch()
        return self.rx_name.search(v).group("name").strip()
