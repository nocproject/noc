# ---------------------------------------------------------------------
# HP.Aruba.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_fqdn import Script as BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN
from noc.core.text import parse_kv


class Script(BaseScript):
    name = "HP.Aruba.get_fqdn"
    interface = IGetFQDN

    parse_map = {
        "hostname": "hostname",
    }

    def execute_cli(self):
        v = self.cli("show system", cached=True)
        v = parse_kv(self.parse_map, v)
        return v["hostname"]
