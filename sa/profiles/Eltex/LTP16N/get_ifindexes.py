# ---------------------------------------------------------------------
# Eltex.LTP16N.get_ifindexes
# ---------------------------------------------------------------------
# Copyright (C) 2024-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetifindexes import IGetIfindexes


class Script(BaseScript):
    name = "Eltex.LTP16N.get_ifindexes"
    interface = IGetIfindexes
    cache = True
    requires = []

    def execute_snmp(self, **kwargs):
        ifname = dict()
        for oid, v in self.snmp.getnext("1.3.6.1.2.1.2.2.1.2", cached=True):
            sindex = oid[len("1.3.6.1.2.1.2.2.1.2") + 1 :]

            if v.split(" ")[0] == "Front-port" or v.split(" ")[0] == "PON-port":
                ifname[v.lower()] = sindex
        return ifname
