# ---------------------------------------------------------------------
# MikroTik.RouterOS.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_fqdn import Script as BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "MikroTik.RouterOS.get_fqdn"
    interface = IGetFQDN
    always_prefer = "S"

    def execute_cli(self):
        s = self.cli("/system identity print")
        if s and "name: " in s:
            return s.split(":", 1)[1].strip()
        return "MikroTik"
