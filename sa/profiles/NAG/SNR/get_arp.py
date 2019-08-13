# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# NAG.SNR.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from builtins import str

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "NAG.SNR.get_arp"
    interface = IGetARP
    cache = True

    def execute_snmp(self):
        r = []
        for v in self.snmp.get_tables(
            ["1.3.6.1.2.1.4.22.1.1", "1.3.6.1.2.1.4.22.1.2", "1.3.6.1.2.1.4.22.1.3"], bulk=True
        ):
            iface = self.snmp.get("1.3.6.1.2.1.31.1.1.1.1." + str(v[1]), cached=True)  # IF-MIB
            mac = ":".join(["%02x" % ord(c) for c in v[2]])
            r.append({"ip": v[3], "mac": mac, "interface": iface})
        return r
