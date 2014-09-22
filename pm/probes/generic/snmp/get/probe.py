## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generic SNMP Get
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.pm.probes.base import Probe, metric


class SNMPGetProbe(Probe):
    TITLE = "SNMP Get"
    DESCRIPTION = "Generic SNMP Get"
    TAGS = ["snmp"]
    CONFIG_FORM = "SNMPGetConfig"

    @metric(["Custom | SNMP | OID"],
            convert=metric.NONE,
            preference=metric.PREF_COMMON)
    def get_oid(self, address, snmp__ro, oid,
                convert=metric.NONE, scale=1.0):
        self.set_convert("Custom | SNMP | OID",
                         convert=convert, scale=float(scale))
        return self.snmp_get(oid, address=address, community=snmp__ro)
