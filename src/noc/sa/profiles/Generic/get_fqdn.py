# ---------------------------------------------------------------------
# Generic.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN
from noc.core.mib import mib


class Script(BaseScript):
    name = "Generic.get_fqdn"
    interface = IGetFQDN

    SNMP_SYSNAME_OID = mib["SNMPv2-MIB::sysName", 0]

    def execute_snmp(self, **kwargs):
        # sysName.0
        v = self.snmp.get(self.get_sysname_oid())
        if v:
            return v
        raise NotImplementedError

    def get_sysname_oid(self):
        return self.SNMP_SYSNAME_OID
