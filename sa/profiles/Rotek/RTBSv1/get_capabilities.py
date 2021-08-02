# ---------------------------------------------------------------------
# Rotek.RTBSv1.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.core.snmp.error import SNMPError
from noc.core.mib import mib


class Script(BaseScript):
    name = "Rotek.RTBSv1.get_capabilities"
    cache = True

    def get_enterprise_id(self, version=None):
        """
        Returns EnterpriseID number from sysObjectID
        :param version:
        :return:
        """
        if self.credentials.get("snmp_ro"):
            try:
                r = self.snmp.get(mib["SNMPv2-MIB::sysORID", 4], version=version)
                if r is None:
                    r = getattr(self, "_ent_id", None)
                elif len(r.split(".")) < 6:
                    # Bad values
                    r = self.snmp.getnext(
                        "1.3.6.1.4.1", bulk=False, version=version, only_first=True
                    )
                    if r:
                        r = r[0][0]
                return r
            except (self.snmp.TimeOutError, SNMPError):
                pass

    # def execute_platform(self, caps):
    # if self.match_version(platform__regex="^WILI*"):
    # caps["CPE | AP"] = True
