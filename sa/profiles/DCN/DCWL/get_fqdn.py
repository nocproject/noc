# ---------------------------------------------------------------------
# DCN.DCWL.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.interfaces.igetfqdn import IGetFQDN
from noc.sa.profiles.Generic.get_fqdn import Script as BaseScript


class Script(BaseScript):
    name = "DCN.DCWL.get_fqdn"
    interface = IGetFQDN

    def execute_snmp(self, **kwargs):
        # device does not support SNMP
        return

    def execute_cli(self, **kwargs):
        """
        get device hostname
        """
        result = ""
        responce = self.cli("get host")
        for line in responce.splitlines():
            sysname_str = line.split(" ", 1)
            if sysname_str[0] == "id":
                result = sysname_str[1].strip()
                break
        return result
