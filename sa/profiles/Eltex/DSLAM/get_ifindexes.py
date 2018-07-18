# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Generic.get_ifindexes
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetifindexes import IGetIfindexes
from noc.core.mib import mib


class Script(BaseScript):
    name = "Eltex.DSLAM.get_ifindexes"
    interface = IGetIfindexes
    cache = True

    def execute_snmp(self):
        r = {}
        if self.is_platform_MXA24:
            o = "1.3.6.1.4.1.34300.1.6"
            ooid = "%s.15.2.1.2" % o
            aoid = "%s.10.2.1.2" % o
            for oid, name in self.snmp.getnext(aoid, max_retries=8):
                if oid.endswith(".0"):
                    ifindex = int(oid.split(".")[-2])
                else:
                    ifindex = int(oid.split(".")[-1])
                r[name] = ifindex
            for oid, name in self.snmp.getnext(ooid, max_retries=8):
                if " " in name:
                    name = name.split()[2]
                if name.startswith("p"):
                    name = "s%s" % name
                if oid.endswith(".0"):
                    ifindex = int(oid.split(".")[-2])
                else:
                    ifindex = int(oid.split(".")[-1])
                r[name] = ifindex
        else:
            if self.is_platform_MXA32:
                o = "1.3.6.1.4.1.35265.1.28"
            else:
                o = "1.3.6.1.4.1.35265.1.33"
            aoid = "%s.10.2.1.2" % o
            for oid, name in self.snmp.getnext(mib["IF-MIB::ifDescr"], max_retries=8):
                if name.startswith("p"):
                    name = "s%s" % name
                ifindex = int(oid.split(".")[-1])
                r[name] = ifindex

            for oid, name in self.snmp.getnext(aoid, max_retries=8):
                if oid.endswith(".0"):
                    ifindex = int(oid.split(".")[-2])
                else:
                    ifindex = int(oid.split(".")[-1])
                r[name] = ifindex

        return r
